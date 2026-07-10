from django.db import models

class TimeSlot(models.Model): # 시간대
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)

    class Meta:
        db_table = 'time_slot' #db 테이블 이름

    def __str__(self):
        return self.name


class Skill(models.Model): # 스킬
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)

    class Meta:
        db_table = 'skill'

    def __str__(self):
        return self.name


class JobCategory(models.Model): # 직무
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)

    class Meta:
        db_table = 'job_category'

    def __str__(self):
        return self.name


class JobSkill(models.Model): # 직무별 스킬
    job_category = models.ForeignKey(
        JobCategory, on_delete=models.CASCADE, related_name='job_skills'
    )
    skill = models.ForeignKey(
        Skill, on_delete=models.CASCADE, related_name='job_skills'
    )

    class Meta:
        db_table = 'job_skill'
        
    def __str__(self):
        return f'{self.job_category} - {self.skill}'


class HiddenAbility(models.Model):  # 숨은 능력
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(
        blank=True,
        help_text='LLM 분류 프롬프트에 그대로 넣을 판단 기준 설명'
    )

    class Meta:
        db_table = 'hidden_ability'

    def __str__(self):
        return self.name


class JobHiddenAbility(models.Model):  # 직무별 숨은능력
    job_category = models.ForeignKey(
        JobCategory, on_delete=models.CASCADE, related_name='job_hidden_abilities'
    )
    hidden_ability = models.ForeignKey(
        HiddenAbility, on_delete=models.CASCADE, related_name='job_hidden_abilities'
    )

    class Meta:
        db_table = 'job_hidden_ability'
        unique_together = ('job_category', 'hidden_ability')

    def __str__(self):
        return f'{self.job_category} - {self.hidden_ability}'
