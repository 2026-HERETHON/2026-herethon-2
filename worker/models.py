from django.db import models
from core.models import JobCategory, TimeSlot, Skill, HiddenAbility
from django.conf import settings

class WorkerProfile(models.Model):
    class CareerYears(models.TextChoices):
        ANY = 'ANY', 'Any'
        ONE_TO_THREE = 'ONE_TO_THREE', '1~3년'
        THREE_TO_FIVE = 'THREE_TO_FIVE', '3~5년'
        FIVE_TO_SEVEN = 'FIVE_TO_SEVEN', '5~7년'
        OVER_SEVEN = 'OVER_SEVEN', '7년 이상'

    class WeeklyHours(models.TextChoices):
        UNDER_15 = 'UNDER_15', '주 15시간 미만'
        FIFTEEN_TO_25 = 'FIFTEEN_TO_25', '주 15시간 ~25시간'
        OVER_25 = 'OVER_25', '주 25시간 이상'

    class WorkStyle(models.TextChoices):
        REMOTE = 'REMOTE', '100%재택'
        ONSITE_WEEKLY_1 = 'ONSITE_WEEKLY_1', '주 1회 출근'
        ONSITE_WEEKLY_3 = 'ONSITE_WEEKLY_3', '주 3회 이상 출근'
        ONSITE_DAILY = 'ONSITE_DAILY', '매일 출근 '
        
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
        help_text="온보딩4: 'WARMUP', 'REAL'" #text 말고 다른 필드들처럼 TextChoices로 수정함
    )

    class Meta:
        db_table = 'worker_profile'

    def __str__(self):
        return f'WorkerProfile({self.user_id})'


class WorkerHiddenActivity(models.Model): #숨은능력
    worker_profile = models.ForeignKey(WorkerProfile, on_delete=models.CASCADE, related_name='hidden_activities')
    activity_text = models.CharField(max_length=300)

    class Meta:
        db_table = 'worker_hidden_activity'


class WorkerCoreTime(models.Model): #코어 시간
    worker_profile = models.ForeignKey(WorkerProfile, on_delete=models.CASCADE, related_name='core_times')
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE, related_name='worker_core_times')

    class Meta:
        db_table = 'worker_core_time'


class WorkerPreferredScale(models.Model): #규모
    class ScaleType(models.TextChoices):
        SHORT = 'SHORT', '1~2주 단기'
        LONG = 'LONG', '1개월 이상 중기'
        REGULAR_TRANSITION = 'REGULAR_TRANSITION', '정규직 전환 전체(리턴십)'

    worker_profile = models.ForeignKey(WorkerProfile, on_delete=models.CASCADE, related_name='preferred_scales')
    scale_type = models.CharField(max_length=30, choices=ScaleType.choices)

    class Meta:
        db_table = 'worker_preferred_scale'


class WorkerConcern(models.Model): #고민
    worker_profile = models.ForeignKey(WorkerProfile, on_delete=models.CASCADE, related_name='concerns')
    concern_text = models.CharField(max_length=255)

    class Meta:
        db_table = 'worker_concern'


class WorkerSkill(models.Model): #스킬
    worker_profile = models.ForeignKey(WorkerProfile, on_delete=models.CASCADE, related_name='worker_skills')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='worker_skills')

    class Meta:
        db_table = 'worker_skill'
        unique_together = ('worker_profile', 'skill') # 동일한 스킬 중복 불가
        
class WorkerCareer(models.Model): 
    worker_profile = models.ForeignKey(
        WorkerProfile, on_delete=models.CASCADE, related_name='careers'
    )
    company_name = models.CharField(max_length=100)
    role_title = models.CharField(max_length=100, null=True, blank=True)
    start_year = models.IntegerField(null=True, blank=True)
    end_year = models.IntegerField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'worker_career'

    def __str__(self):
        return f'{self.company_name} ({self.role_title or "N/A"})'
    
    
class WorkerHiddenAbilityResult(models.Model):
    worker_profile = models.ForeignKey(
        WorkerProfile, on_delete=models.CASCADE, related_name='hidden_ability_results'
    )
    hidden_ability = models.ForeignKey( #번역된 능력
        'core.HiddenAbility', on_delete=models.CASCADE, related_name='worker_results'
    )
    source_activity = models.ForeignKey( #원본 능력(공백기)
        WorkerHiddenActivity, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='converted_results'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'worker_hidden_ability_result'

    def __str__(self):
        return f'{self.worker_profile_id} - {self.hidden_ability}'