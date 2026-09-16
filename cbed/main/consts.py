from enum import Enum


class LevelNames(str, Enum):
    MBE_LEVEL_DRILLS = "MBE Level Drills"
    FL_MCQ_DRILLS = "FL MCQ Drills"
    CA_MCQ_DRILLS = "CA MCQ Drills"
    MPRE_DRILLS = "MPRE Drills"
    NG_MCQ_1_CHOICE = "NG 1-Choice MCQ"
    NG_MCQ_2_CHOICE = "NG 2-Choice MCQ"
    # Agency
    AGENCY_LEVEL = "Agency"
    # Partnerships
    PARTNERSHIPS_LEVEL = "Partnerships"
    # Corps
    CORPS_LEVEL = "Corps"
    # Conflicts
    CONFLICTS_LEVEL = "Conflicts"
    # Fam Law
    FAM_LAW_LEVEL = "Fam Law"
    # Trusts
    TRUSTS_LEVEL = "Trusts"
    # Wills
    WILLS_LEVEL = "Wills"
    # Sec Trans
    SEC_TRANS_LEVEL = "Sec Trans"
    # IQS Drafting Sets
    DRAFTING_SETS = "IQS Drafting Sets"
    # IQS Counseling Sets
    COUNSELING_SETS = "IQS Counseling Sets"
    # Standard Performance Tasks
    STANDARD_PERF_TASKS = "Standard Perf Tasks"
    # Long-Run Performance Tasks (LRPT)
    LRPTS = "LRPTs"
    # Mixed MBE Sets
    MIXED_MBE_SETS = "Mixed MBE Sets"
