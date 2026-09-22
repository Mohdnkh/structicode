"""Read-only versioned view of software capability truth."""

from fastapi import APIRouter, HTTPException

from .domain.design_code_registry import (
    CapabilityListResponse, FamilyCapability, get_family, list_families,
)


router = APIRouter(prefix="/api/v1/capabilities", tags=["v1 capabilities"])


@router.get("", response_model=CapabilityListResponse)
def list_capabilities() -> CapabilityListResponse:
    return CapabilityListResponse(families=list_families())


@router.get("/{family_id}", response_model=FamilyCapability)
def family_capability(family_id: str) -> FamilyCapability:
    family = get_family(family_id)
    if family is None:
        raise HTTPException(status_code=404, detail="Unknown design-code family")
    return family
