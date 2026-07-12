from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from django import forms
from django.conf import settings

from business_os.apps.catalogue.models import Offering, OfferingVariant
from business_os.apps.core.models import RecordStatus
from business_os.apps.organizations.facility_profiles import FacilityProfile
from business_os.apps.organizations.models import Facility, Organization

OFFERING_CODE_PATTERN = re.compile(r"^[A-Z0-9][A-Z0-9._-]{0,79}$")


@dataclass(frozen=True)
class OfferingFormSchema:
    """Facility-aware schema for the first Business Admin offering form."""

    page_title: str
    eyebrow: str
    submit_label: str
    offering_type: str
    labels: dict[str, str]
    help_texts: dict[str, str]


def resolve_offering_form_schema(
    *,
    facility_profile: FacilityProfile,
    mode: str = "create",
) -> OfferingFormSchema:
    offering = facility_profile.terms["offering"]
    offerings = facility_profile.terms["offerings"]
    offering_lower = offering.lower()
    is_edit = mode == "edit"

    return OfferingFormSchema(
        page_title=f"{'Edit' if is_edit else 'Add'} {offering_lower}",
        eyebrow=f"{offerings} / {'Edit' if is_edit else 'New'}",
        submit_label=f"{'Save' if is_edit else 'Create'} {offering_lower}",
        offering_type=_offering_type_for_facility(facility_profile),
        labels={
            "name": f"{offering} name",
            "code": f"{offering} code / SKU",
            "summary": f"{offering} summary",
            "description": f"{offering} description",
            "base_price": "Base price",
            "currency": "Currency",
            "status": "Publishing status",
            "visible_on_website": "Visible on website",
            "whatsapp_inquiry_enabled": "Allow WhatsApp inquiry",
        },
        help_texts={
            "code": (
                "Use a stable internal code. Letters, numbers, dots, hyphens, "
                "and underscores are supported."
            ),
            "summary": f"Short optional summary shown in {offering_lower} cards.",
            "description": f"Longer optional description for the {offering_lower} detail page.",
            "status": (
                "Published offerings are available to public website and checkout flows "
                "when visible."
            ),
            "visible_on_website": "Turn this off to keep the offering available internally only.",
            "whatsapp_inquiry_enabled": (
                "Allows customer inquiry flows where the catalogue module supports them."
            ),
        },
    )


class OfferingAdminForm(forms.Form):
    name = forms.CharField(max_length=180)
    code = forms.CharField(max_length=80)
    summary = forms.CharField(max_length=255, required=False)
    description = forms.CharField(required=False, widget=forms.Textarea)
    base_price = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0.00"),
    )
    currency = forms.ChoiceField(choices=())
    status = forms.ChoiceField(
        choices=(
            (RecordStatus.ACTIVE, "Publish now"),
            (RecordStatus.DRAFT, "Save as draft"),
        ),
    )
    visible_on_website = forms.BooleanField(required=False, initial=True)
    whatsapp_inquiry_enabled = forms.BooleanField(required=False, initial=True)

    def __init__(
        self,
        *args: Any,
        organization: Organization,
        facility_profile: FacilityProfile,
        instance: Offering | None = None,
        **kwargs: Any,
    ) -> None:
        self.organization = organization
        self.facility_profile = facility_profile
        self.instance = instance
        self.schema = resolve_offering_form_schema(
            facility_profile=facility_profile,
            mode="edit" if instance is not None else "create",
        )
        if instance is not None and not args and "initial" not in kwargs:
            kwargs["initial"] = _initial_for_offering(instance)
        super().__init__(*args, **kwargs)

        self.fields["currency"].choices = [
            (currency, currency) for currency in settings.SUPPORTED_CURRENCIES
        ]
        self.fields["currency"].initial = organization.default_currency
        self.fields["status"].initial = RecordStatus.ACTIVE

        for name, label in self.schema.labels.items():
            self.fields[name].label = label
        for name, help_text in self.schema.help_texts.items():
            self.fields[name].help_text = help_text

        self._apply_widget_classes()

    def clean_code(self) -> str:
        code = self.cleaned_data["code"].strip().upper()
        if not OFFERING_CODE_PATTERN.fullmatch(code):
            raise forms.ValidationError(
                "Use letters, numbers, dots, hyphens, or underscores, "
                "starting with a letter or number."
            )

        offering_conflicts = Offering.objects.filter(
            organization=self.organization,
            code__iexact=code,
        )
        if self.instance is not None:
            offering_conflicts = offering_conflicts.exclude(id=self.instance.id)
        if offering_conflicts.exists():
            offering = self.facility_profile.terms["offering"].lower()
            raise forms.ValidationError(f"A {offering} with this code already exists.")

        variant_conflicts = OfferingVariant.objects.filter(
            organization=self.organization,
            sku__iexact=code,
        )
        default_variant = _default_variant_for_offering(self.instance)
        if default_variant is not None:
            variant_conflicts = variant_conflicts.exclude(id=default_variant.id)
        if variant_conflicts.exists():
            raise forms.ValidationError("A variant with this SKU already exists.")
        return code

    def clean_currency(self) -> str:
        return self.cleaned_data["currency"].strip().upper()

    def to_service_kwargs(self) -> dict[str, Any]:
        status = self.cleaned_data["status"]
        return {
            "name": self.cleaned_data["name"].strip(),
            "code": self.cleaned_data["code"],
            "summary": self.cleaned_data["summary"].strip(),
            "description": self.cleaned_data["description"].strip(),
            "base_price": self.cleaned_data["base_price"],
            "currency": self.cleaned_data["currency"],
            "status": status,
            "visible_on_website": self.cleaned_data["visible_on_website"],
            "whatsapp_inquiry_enabled": self.cleaned_data["whatsapp_inquiry_enabled"],
            "offering_type": self.schema.offering_type,
        }

    def _apply_widget_classes(self) -> None:
        input_class = "input input-bordered w-full"
        textarea_class = "textarea textarea-bordered min-h-28 w-full"
        select_class = "select select-bordered w-full"
        checkbox_class = "checkbox checkbox-primary"

        for field_name in ("name", "code", "summary", "base_price", "currency", "status"):
            self.fields[field_name].widget.attrs.setdefault(
                "class",
                select_class if field_name in {"currency", "status"} else input_class,
            )
        self.fields["description"].widget.attrs.setdefault("class", textarea_class)
        self.fields["description"].widget.attrs.setdefault("rows", 5)
        self.fields["visible_on_website"].widget.attrs.setdefault("class", checkbox_class)
        self.fields["whatsapp_inquiry_enabled"].widget.attrs.setdefault("class", checkbox_class)


def _offering_type_for_facility(facility_profile: FacilityProfile) -> str:
    if facility_profile.facility_type == Facility.FacilityType.OFFICE:
        return Offering.OfferingType.SERVICE
    return Offering.OfferingType.PRODUCT


def _initial_for_offering(offering: Offering) -> dict[str, Any]:
    return {
        "name": offering.name,
        "code": offering.code,
        "summary": offering.summary,
        "description": offering.description,
        "base_price": offering.base_price,
        "currency": offering.currency,
        "status": offering.status,
        "visible_on_website": offering.visible_on_website,
        "whatsapp_inquiry_enabled": offering.whatsapp_inquiry_enabled,
    }


def _default_variant_for_offering(offering: Offering | None) -> OfferingVariant | None:
    if offering is None or offering.pk is None:
        return None
    return (
        OfferingVariant.objects.filter(
            organization=offering.organization,
            offering=offering,
            is_default=True,
        )
        .order_by("created_at")
        .first()
    )
