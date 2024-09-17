from enum import Enum


class LevelNames(str, Enum):
    MBE_LEVEL_DRILLS = "MBE Level Drills"
    FL_MCQ_DRILLS = "FL MCQ Drills"
    CA_MCQ_DRILLS = "CA MCQ Drills"
    MPRE_DRILLS = "MPRE Drills"
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
