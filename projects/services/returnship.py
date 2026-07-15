from django.core.exceptions import ValidationError

from projects.models import Application, Project, Returnship


def create_returnship_offer(*, application, title, content):
    if application.project.status != Project.Status.COMPLETED:
        raise ValidationError('완료된 프로젝트의 참여자에게만 제안할 수 있어요.')

    if application.status != Application.Status.ACCEPTED:
        raise ValidationError('수락된 지원자에게만 제안할 수 있어요.')

    if not title.strip() or not content.strip():
        raise ValidationError('제목과 제안 내용을 모두 입력해주세요.')

    if Returnship.objects.filter(application=application).exists():
        raise ValidationError('이미 이 참여자에게 리턴십을 제안했어요.')

    return Returnship.objects.create(
        application=application,
        title=title.strip(),
        content=content.strip(),
    )