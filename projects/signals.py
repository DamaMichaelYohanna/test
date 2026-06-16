from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Project, ProjectLifecycleStage

@receiver(post_save, sender=Project)
def populate_project_lifecycle_stages(sender, instance, created, **kwargs):
    """
    Automatically generates your exact organizational framework steps 
    the moment a new project entry is initiated.
    """
    if not created:
        return  # Only run this automation when the project is first created

    # Base Core Steps common to ALL projects (Bidding and Pre-Award)
    core_pre_award_steps = [
        "Appropriation: List Acquisition (List of Projects)",
        "Company Selection & Alignment",
        "Compliance: Documents Renewal and Harmonization",
        "BOQ Development & Internal Review",
        "Procurement Process: Bi-weekly Purchase of the Federal Tender Journal",
        "Company Profile Preparation and Update",
        "Technical Submission and Opening",
        "BOQ Acquisition from the Agency or Sharing of In-House BOQs with the Agency for Regularization",
        "Financial Submission and Opening",
        "Follow-up with the Agency on Award Letters",
        "Collection of Award Letters",
        "Acceptance Letter Preparation and Submission",
        "Mobilization Request Development and Submission",
        "Bonds Preparation and Submission (0.3%–0.4% processing calculation)",
        "Mobilization Batch Number Acquisition and Collation",
        "Submission of Batch Numbers to the AGF's Office and Follow-up on Payments",
    ]

    # Contextual steps unique to Construction/Civil engineering execution
    construction_steps = [
        "Site Assessment and Handover to the Winning Company by the Agency",
        "Site Allocation to Sub-Contractors",
        "Request for Sub-Contractor BOQs",
        "Project Execution Cost Negotiations with Sub-Contractors",
        "Agreement Signing by Sub-Contractors",
        "Mobilization to Site",
        "Project Milestone Monitoring (Agreement Compliance Framework)",
        "Project Completion Audit",
    ]

    # Contextual steps unique to Supply and Training programs
    supply_training_steps = [
        "Special Duties and Agency Inspection of Supplied Items",
        "Training Activities Execution & Attendance Logging",
    ]

    # Final Post-Execution/Treasury steps common to ALL contracts
    treasury_payment_steps = [
        "Application for Payment: Internal Assessment by Special Duties & Agency",
        "Internal Processing Stage: Head of Audit Office Review",
        "Internal Processing Stage: Procurement Office Verification",
        "Internal Processing Stage: Store Department Issuance/Logistics",
        "Internal Processing Stage: Director of Finance Clearance",
        "Follow up with Agency on Internal Project File Movement",
        "Confirmation of Payment Upload Status (Certified Status Verification)",
        "Final Payment Batch Number Acquisition and Collation",
        "Submission of Final Batch Numbers to the AGF's Office and Follow-up on Payments",
    ]

    # Compile the final roadmap list based on what type the user selected
    final_lifecycle_map = []
    final_lifecycle_map.extend(core_pre_award_steps)
    
    if instance.project_type == 'CONSTRUCTION':
        final_lifecycle_map.extend(construction_steps)
    else:
        final_lifecycle_map.extend(supply_training_steps)
        
    final_lifecycle_map.extend(treasury_payment_steps)

    # Bulk insert the items into the database table rows sequentially
    stages_to_create = [
        ProjectLifecycleStage(
            project=instance,
            stage_name=step_name,
            sequence_order=index + 1
        )
        for index, step_name in enumerate(final_lifecycle_map)
    ]
    
    ProjectLifecycleStage.objects.bulk_create(stages_to_create)