from django.db import models
from core.models import JobCategory, TimeSlot, Skill, HiddenAbility
from django.conf import settings

class WorkerProfile(models.Model):
    class CareerYears(models.TextChoices):
        ONE_TO_THREE = 'ONE_TO_THREE', '1~3년'
        THREE_TO_FIVE = 'THREE_TO_FIVE', '3~5년'
        FIVE_TO_SEVEN = 'FIVE_TO_SEVEN', '5~7년'
        OVER_SEVEN = 'OVER_SEVEN', '7년 이상'

    class WeeklyHours(models.TextChoices):
        UNDER_15 = 'UNDER_15', '주 15시간 미만'
        FIFTEEN_TO_25 = 'FIFTEEN_TO_25', '주 15시간~25시간'
        OVER_25 = 'OVER_25', '주 25시간 이상'

    class WorkStyle(models.TextChoices):
        REMOTE = 'REMOTE', '100% 재택'
        ONSITE_WEEKLY_1 = 'ONSITE_WEEKLY_1', '주 1회 출근'
        ONSITE_WEEKLY_3 = 'ONSITE_WEEKLY_3', '주 3회 이상 출근'
        ONSITE_DAILY = 'ONSITE_DAILY', '매일 출근'
        
    class ApplicationType(models.TextChoices): #지원 유형
        WARMUP = 'WARMUP', '워밍업 프로젝트'
        REAL = 'REAL', '실무 프로젝트'

    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='worker_profile')
    job_category = models.ForeignKey(JobCategory, on_delete=models.CASCADE, related_name='worker_profiles')
    career_years = models.CharField(max_length=20, choices=CareerYears.choices, help_text='온보딩2 연차 선택')
    achievement_keywords = models.CharField(max_length=500, null=True, blank=True, help_text='온보딩2')
    weekly_hours = models.CharField(max_length=20, choices=WeeklyHours.choices, help_text='온보딩3')
    preferred_work_style = models.CharField(max_length=20, choices=WorkStyle.choices, help_text='온보딩3')
    created_at = models.DateTimeField(auto_now_add=True)
    application_type = models.CharField(
        max_length=50,
        choices=ApplicationType.choices,
        null=True, blank=True,
        help_text="온보딩4: 'WARMUP', 'REAL'"
    )

    class Meta:
        db_table = 'worker_profile'

    def __str__(self):
        return f'WorkerProfile({self.user_id})'


class WorkerHiddenActivity(models.Model): #공백기 활동
    worker_profile = models.ForeignKey(WorkerProfile, on_delete=models.CASCADE, related_name='hidden_activities')
    hidden_ability = models.ForeignKey(HiddenAbility, on_delete=models.CASCADE, null=True, blank=True, related_name='hidden_activities')
    activity_text = models.CharField(max_length=300)

    class Meta:
        db_table = 'worker_hidden_activity'


class WorkerCoreTime(models.Model): #코어 시간
    worker_profile = models.ForeignKey(WorkerProfile, on_delete=models.CASCADE, related_name='core_times')
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE, related_name='worker_core_times')

    class Meta:
        db_table = 'worker_core_time'
        unique_together = ('worker_profile', 'time_slot')


class WorkerPreferredScale(models.Model): #규모
    class ScaleType(models.TextChoices):
        SHORT = 'SHORT', '1~2주 단기'
        LONG = 'LONG', '1개월 이상 중기'
        REGULAR_TRANSITION = 'REGULAR_TRANSITION', '정규직 전환 전제(리턴십)'

    worker_profile = models.ForeignKey(WorkerProfile, on_delete=models.CASCADE, related_name='preferred_scales')
    scale_type = models.CharField(max_length=30, choices=ScaleType.choices)

    class Meta:
        db_table = 'worker_preferred_scale'
        unique_together = ('worker_profile', 'scale_type')


class WorkerConcern(models.Model):  #고민
    class ConcernType(models.TextChoices):
        DIGITAL_SKILL = 'DIGITAL_SKILL', '최신 트렌드·지식 부족'
        COMMUNICATION = 'COMMUNICATION', '커뮤니케이션 자신감 저하'
        PHYSICAL_BURDEN = 'PHYSICAL_BURDEN', '체력적인 부담'
        CHILDCARE = 'CHILDCARE', '가사 병행의 어려움'
        CAREER_GAP_ANXIETY = 'CAREER_GAP_ANXIETY', '경력 공백에 대한 시선'

    worker_profile = models.ForeignKey(
        WorkerProfile, on_delete=models.CASCADE, related_name='concerns'
    )
    concern_type = models.CharField(max_length=30, choices=ConcernType.choices)

    class Meta:
        db_table = 'worker_concern'
        unique_together = ('worker_profile', 'concern_type')

    def __str__(self):
        return f'{self.worker_profile_id} - {self.concern_type}'


class WorkerSkill(models.Model): #스킬
    worker_profile = models.ForeignKey(WorkerProfile, on_delete=models.CASCADE, related_name='worker_skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='worker_skills')

    class Meta:
        db_table = 'worker_skill'
        unique_together = ('worker_profile', 'skill') # 동일한 스킬 중복 불가