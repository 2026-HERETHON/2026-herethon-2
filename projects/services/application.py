from pathlib import Path

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from projects.models import Application, ApplicationFile, Project


ALLOWED_EXTENSIONS = {
    '.pdf',
    '.ppt',
    '.pptx',
    '.jpg',
    '.jpeg',
    '.png',
}

MAX_FILE_COUNT = 5
MAX_FILE_SIZE = 10 * 1024 * 1024


def validate_application_files(files):
    if len(files) > MAX_FILE_COUNT:
        raise ValidationError('첨부파일은 최대 5개까지 등록할 수 있습니다.')

    for uploaded_file in files:
        extension = Path(uploaded_file.name).suffix.lower()

        if extension not in ALLOWED_EXTENSIONS:
            raise ValidationError(
                f'{uploaded_file.name}: 지원하지 않는 파일 형식입니다.'
            )

        if uploaded_file.size > MAX_FILE_SIZE:
            raise ValidationError(
                f'{uploaded_file.name}: 파일 크기는 10MB 이하여야 합니다.'
            )


# 지원 기능 관련 로직
@transaction.atomic
def create_application(*, project, worker_profile, files):
    project = Project.objects.select_for_update().get(pk=project.pk)

    today = timezone.localdate()

    if project.status != Project.Status.OPEN:
        raise ValidationError('현재 모집 중인 프로젝트가 아닙니다.')

    if project.deadline < today:
        project.status = Project.Status.SELECTING
        project.save(update_fields=['status'])
        raise ValidationError('지원 마감일이 지난 프로젝트입니다.')

    if Application.objects.filter(
        project=project,
        worker_profile=worker_profile,
    ).exists():
        raise ValidationError('이미 지원한 프로젝트입니다.')

    validate_application_files(files)

    application = Application.objects.create(
        project=project,
        worker_profile=worker_profile,
        status=Application.Status.PENDING,
    )

    for uploaded_file in files:
        ApplicationFile.objects.create(
            application=application,
            file=uploaded_file,
            original_name=uploaded_file.name,
        )

    return application