from django.db import models
from core.models import JobCategory, Skill, TimeSlot, HiddenAbility


class Project(models.Model):
    class ProjectType(models.TextChoices):
        WARMUP = 'WARMUP', '워밍업'
        REAL = 'REAL', '실무'

    class WorkStyle(models.TextChoices):
        REMOTE = 'REMOTE', '100% 재택'
        ONSITE_WEEKLY_1 = 'ONSITE_WEEKLY_1', '주 1회 출근'
        ONSITE_WEEKLY_3 = 'ONSITE_WEEKLY_3', '주 3회 이상 출근'
        ONSITE_DAILY = 'ONSITE_DAILY', '매일 출근'

    class WeeklyHours(models.TextChoices):
        UNDER_15 = 'UNDER_15', '주 15시간 미만'
        FIFTEEN_TO_25 = 'FIFTEEN_TO_25', '주 15시간~25시간'
        OVER_25 = 'OVER_25', '주 25시간 이상'

    class CareerYears(models.TextChoices):
        ONE_TO_THREE = 'ONE_TO_THREE', '1~3년'
        THREE_TO_FIVE = 'THREE_TO_FIVE', '3~5년'
        FIVE_TO_SEVEN = 'FIVE_TO_SEVEN', '5~7년'
        OVER_SEVEN = 'OVER_SEVEN', '7년 이상'

    class Status(models.TextChoices):
        OPEN = 'OPEN', '모집중'
        SELECTING = 'SELECTING', '선발중'
        IN_PROGRESS = 'IN_PROGRESS', '진행중'
        COMPLETED = 'COMPLETED', '완료'

    company_profile = models.ForeignKey(
        'company.CompanyProfile', on_delete=models.CASCADE, related_name='projects'
    )
    job_category = models.ForeignKey(
        JobCategory, on_delete=models.CASCADE, related_name='projects'
    )
    project_type = models.CharField(max_length=20, choices=ProjectType.choices)
    title = models.CharField(max_length=200)
    work_style = models.CharField(max_length=20, choices=WorkStyle.choices)
    weekly_hours = models.CharField(max_length=20, choices=WeeklyHours.choices)
    compensation_amount = models.IntegerField()
    deadline = models.DateField()
    description = models.TextField()
    duration = models.CharField(max_length=100, null=True, blank=True)
    recruitment_count = models.IntegerField()
    career_years = models.CharField(max_length=20, choices=CareerYears.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    view_count = models.IntegerField(default=0)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'project'

    def __str__(self):
        return self.title


class ProjectSkill(models.Model):  # 프로젝트 스킬 (필수/우대)
    class Priority(models.TextChoices):
        NORMAL = 'NORMAL', '필수'
        PREFERRED = 'PREFERRED', '우대'

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name='project_skills'
    )
    skill = models.ForeignKey(
        Skill, on_delete=models.CASCADE, related_name='project_skills'
    )
    priority = models.CharField(max_length=20, choices=Priority.choices)

    class Meta:
        db_table = 'project_skill'
        unique_together = ('project', 'skill')

    def __str__(self):
        return f'{self.project_id} - {self.skill} ({self.priority})'


class ProjectCoreTime(models.Model):  # 코어타임
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name='core_times'
    )
    time_slot = models.ForeignKey(
        TimeSlot, on_delete=models.CASCADE, related_name='project_core_times'
    )

    class Meta:
        db_table = 'project_core_time'
        unique_together = ('project', 'time_slot')

    def __str__(self):
        return f'{self.project_id} - {self.time_slot}'


class ProjectPreferredScale(models.Model):  # 프로젝트 선호 업무 규모
    class ScaleType(models.TextChoices):
        SHORT = 'SHORT', '1~2주 단기'
        LONG = 'LONG', '1개월 이상 중기'
        REGULAR_TRANSITION = 'REGULAR_TRANSITION', '정규직 전환 전제(리턴십)'

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name='preferred_scales'
    )
    scale_type = models.CharField(max_length=30, choices=ScaleType.choices)

    class Meta:
        db_table = 'project_preferred_scale'
        unique_together = ('project', 'scale_type')

    def __str__(self):
        return f'{self.project_id} - {self.scale_type}'


class ProjectHiddenAbility(models.Model):  # 프로젝트 숨은능력
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name='hidden_abilities'
    )
    hidden_ability = models.ForeignKey(
        HiddenAbility, on_delete=models.CASCADE, related_name='project_hidden_abilities'
    )

    class Meta:
        db_table = 'project_hidden_ability'
        unique_together = ('project', 'hidden_ability')

    def __str__(self):
        return f'{self.project_id} - {self.hidden_ability}'


class Application(models.Model):  # 프로젝트 지원
    class Status(models.TextChoices):
        PENDING = 'PENDING', '검토중'
        ACCEPTED = 'ACCEPTED', '수락'
        REJECTED = 'REJECTED', '거절'

    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name='applications'
    )
    worker_profile = models.ForeignKey(
        'worker.WorkerProfile', on_delete=models.CASCADE, related_name='applications'
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    applied_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'application'
        unique_together = ('project', 'worker_profile')

    def __str__(self):
        return f'{self.worker_profile_id} → {self.project_id} ({self.status})'


class ApplicationFile(models.Model):  # 지원 첨부파일 (최대 5개, 종류 구분 없음)
    application = models.ForeignKey(
        Application, on_delete=models.CASCADE, related_name='files'
    )
    file_url = models.CharField(max_length=500)
    original_name = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'application_file'

    def __str__(self):
        return self.original_name


class Returnship(models.Model):  # 리턴십 제안
    class Status(models.TextChoices):
        PENDING = 'PENDING', '응답대기'
        ACCEPTED = 'ACCEPTED', '수락'
        REJECTED = 'REJECTED', '거절'

    application = models.OneToOneField(
        Application, on_delete=models.CASCADE, related_name='returnship'
    )
    title = models.CharField(max_length=200)
    content = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'returnship_offer'

    def __str__(self):
        return f'{self.application_id} - {self.title}'
