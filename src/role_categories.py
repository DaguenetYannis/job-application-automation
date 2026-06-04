from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RoleCategory:
    slug: str
    label: str


ROLE_CATEGORIES: tuple[RoleCategory, ...] = (
    RoleCategory("01_data_analyst", "Data Analyst"),
    RoleCategory("02_bi_reporting_analytics", "BI, Reporting, Analytics"),
    RoleCategory("03_public_policy_statistics", "Public Policy Statistics"),
    RoleCategory("04_economist_policy_analyst", "Economist And Policy Analyst"),
    RoleCategory("05_climate_transition_sustainability", "Climate Transition And Sustainability"),
    RoleCategory("06_industrial_policy_competition", "Industrial Policy And Competition"),
    RoleCategory("07_research_data_science", "Research Data Science"),
    RoleCategory("08_public_sector_consulting", "Public Sector Consulting"),
    RoleCategory("09_international_organizations", "International Organizations"),
)
