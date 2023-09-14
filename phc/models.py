from django.db import models

class County(models.Model):
    name = models.CharField(max_length=100, unique=True)
    progress = models.FloatField(default=0.0, verbose_name="Progress (%)")

    def __str__(self):
        return self.name
    
    def get_subcounties(self):
        # Access and return the related subcounties
        return self.subcounty_set.all()
    
class Partners(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


    
class Subcounty(models.Model):
    county = models.ForeignKey(County, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, unique=True)
    partners = models.ManyToManyField(Partners, blank=True)

    # Step 1 fields
    chmt_meeting = models.BooleanField(default=False, verbose_name="Has CHMT meeting taken place?")
    schmt_hf_staff_meeting = models.BooleanField(default=False, verbose_name="Has the SCHMT & HF staff meeting taken place?")

    # Step 2 fields
    health_facility_assessments = models.BooleanField(default=False, verbose_name="Have Health Facility assessments taken place – using the 6 building blocks?")
    client_exit_surveys = models.BooleanField(default=False, verbose_name="Have client exit surveys taken place?")
    chu_functionality_assessments = models.BooleanField(default=False, verbose_name="Have the CHU functionality assessments taken place?")

    # Step 3 fields
    mapping_hubs_spokes = models.BooleanField(default=False, verbose_name="Has the mapping of the hubs and spokes taken place (Step 3)?")
    training_mdt = models.BooleanField(default=False, verbose_name="Has the training of multi-disciplinary teams (MDTs) taken place (Step 3)?")
    customised_performance_indicators = models.BooleanField(default=False, verbose_name="Have the performance indicators been customized (Step 3)?")
    set_phc_interventions = models.BooleanField(default=False, verbose_name="Have the key PHC interventions been set (Step 3)?")

    # Step 4 fields
    dispensarization = models.BooleanField(default=False, verbose_name="Dispensarization (health status profiling) (Step 4)?")
    multi_stakeholder_engagement = models.BooleanField(default=False, verbose_name="Multi-stakeholder engagement (Step 4)?")
    mdt_roving_healthcare_provision = models.BooleanField(default=False, verbose_name="MDT roving healthcare provision (Step 4)?")
    support_supervision_mentorships = models.BooleanField(default=False, verbose_name="Support supervision & mentorships (Step 4)?")
    m_e_learning_scale = models.BooleanField(default=False, verbose_name="M&E, Learning & scale (Step 4)?")

    # Stage fields
    stage1 = models.BooleanField(default=False, verbose_name="Stage 1")
    stage2 = models.BooleanField(default=False, verbose_name="Stage 2")
    stage3 = models.BooleanField(default=False, verbose_name="Stage 3")
    stage4 = models.BooleanField(default=False, verbose_name="Stage 4")

    progress = models.FloatField(default=0.0, verbose_name="Progress (%)")

    def __str__(self):
        return self.name
