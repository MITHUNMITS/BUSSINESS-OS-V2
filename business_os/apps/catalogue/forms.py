from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from django import forms
from django.conf import settings
from django.db.models import Q
from django.utils.text import slugify

from business_os.apps.catalogue.models import (
    Category,
    Collection,
    Offering,
    OfferingVariant,
    OptionDefinition,
    OptionValue,
)
from business_os.apps.core.models import RecordStatus
from business_os.apps.organizations.facility_profiles import FacilityProfile
from business_os.apps.organizations.models import Facility, Organization

OFFERING_CODE_PATTERN = re.compile(r"^[A-Z0-9][A-Z0-9._-]{0,79}$")
OPTION_CODE_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{0,79}$")
COLOR_HEX_PATTERN = re.compile(r"^#[0-9A-Fa-f]{6}$")


@dataclass(frozen=True)
class OfferingFormSchema:
    """Facility-aware schema for the first Business Admin offering form."""

    page_title: str
    eyebrow: str
    submit_label: str
    offering_type: str
    labels: dict[str, str]
    help_texts: dict[str, str]


@dataclass(frozen=True)
class CategoryFormSchema:
    """Facility-aware schema for the first Business Admin category form."""

    page_title: str
    eyebrow: str
    submit_label: str
    labels: dict[str, str]
    help_texts: dict[str, str]


@dataclass(frozen=True)
class CollectionFormSchema:
    """Facility-aware schema for the first Business Admin collection form."""

    page_title: str
    eyebrow: str
    submit_label: str
    labels: dict[str, str]
    help_texts: dict[str, str]


@dataclass(frozen=True)
class OptionFormSchema:
    """Facility-aware schema for catalogue option definitions."""

    page_title: str
    eyebrow: str
    submit_label: str
    labels: dict[str, str]
    help_texts: dict[str, str]


@dataclass(frozen=True)
class OptionValueFormSchema:
    """Facility-aware schema for catalogue option values."""

    page_title: str
    eyebrow: str
    submit_label: str
    labels: dict[str, str]
    help_texts: dict[str, str]


@dataclass(frozen=True)
class VariantFormSchema:
    """Facility-aware schema for explicit offering variants."""

    page_title: str
    eyebrow: str
    submit_label: str
    labels: dict[str, str]
    help_texts: dict[str, str]


def resolve_offering_form_schema(
    *,
    facility_profile: FacilityProfile,
    mode: str = "create",
) -> OfferingFormSchema:
    offering = facility_profile.terms["offering"]
    offerings = facility_profile.terms["offerings"]
    category = facility_profile.terms["category"]
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
            "category": category,
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
            "category": f"Optional {category.lower()} used to organize this {offering_lower}.",
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


def resolve_collection_form_schema(
    *,
    facility_profile: FacilityProfile,
    mode: str = "create",
) -> CollectionFormSchema:
    offerings = facility_profile.terms["offerings"]
    is_edit = mode == "edit"

    return CollectionFormSchema(
        page_title=f"{'Edit' if is_edit else 'Add'} collection",
        eyebrow=f"Collections / {'Edit' if is_edit else 'New'}",
        submit_label=f"{'Save' if is_edit else 'Create'} collection",
        labels={
            "name": "Collection name",
            "slug": "Collection URL slug",
            "description": "Collection description",
            "offerings": f"{offerings} in collection",
            "status": "Publishing status",
        },
        help_texts={
            "slug": (
                "Optional public URL-safe slug for this collection. "
                "Leave blank to generate one from the name."
            ),
            "description": "Optional description used to explain this curated group.",
            "offerings": f"Select the {offerings.lower()} that belong in this collection.",
            "status": "Active collections are ready for use; drafts stay internal.",
        },
    )


def resolve_category_form_schema(
    *,
    facility_profile: FacilityProfile,
    mode: str = "create",
) -> CategoryFormSchema:
    category = facility_profile.terms["category"]
    categories = facility_profile.terms["categories"]
    category_lower = category.lower()
    is_edit = mode == "edit"

    return CategoryFormSchema(
        page_title=f"{'Edit' if is_edit else 'Add'} {category_lower}",
        eyebrow=f"{categories} / {'Edit' if is_edit else 'New'}",
        submit_label=f"{'Save' if is_edit else 'Create'} {category_lower}",
        labels={
            "name": f"{category} name",
            "slug": f"{category} URL slug",
            "parent": f"Parent {category.lower()}",
            "description": f"{category} description",
            "sort_order": "Sort order",
            "status": "Publishing status",
        },
        help_texts={
            "slug": (
                f"Optional public URL-safe slug for this {category_lower}. "
                "Leave blank to generate one from the name."
            ),
            "parent": f"Optional parent {category_lower} for a simple hierarchy.",
            "description": f"Optional internal and public description for this {category_lower}.",
            "sort_order": "Lower numbers appear first in admin and public catalogue lists.",
            "status": "Active categories are ready for use; drafts stay internal.",
        },
    )


def resolve_option_form_schema(*, mode: str = "create") -> OptionFormSchema:
    is_edit = mode == "edit"
    return OptionFormSchema(
        page_title=f"{'Edit' if is_edit else 'Add'} option",
        eyebrow=f"Options / {'Edit' if is_edit else 'New'}",
        submit_label=f"{'Save' if is_edit else 'Create'} option",
        labels={
            "name": "Option name",
            "code": "Option code",
            "sort_order": "Sort order",
            "status": "Status",
        },
        help_texts={
            "code": "Use a stable lowercase code such as size, color, or material.",
            "sort_order": "Lower numbers appear first when options are shown.",
            "status": "Active options can be used for new variants; drafts stay internal.",
        },
    )


def resolve_option_value_form_schema(
    *,
    option: OptionDefinition,
    mode: str = "create",
) -> OptionValueFormSchema:
    is_edit = mode == "edit"
    return OptionValueFormSchema(
        page_title=f"{'Edit' if is_edit else 'Add'} {option.name.lower()} value",
        eyebrow=f"{option.name} / {'Edit' if is_edit else 'New value'}",
        submit_label=f"{'Save' if is_edit else 'Create'} value",
        labels={
            "label": "Value label",
            "value": "Value code",
            "color_hex": "Color swatch",
            "sort_order": "Sort order",
            "status": "Status",
        },
        help_texts={
            "value": "Use a stable lowercase code for imports, filters, and variant matching.",
            "color_hex": "Optional hex color such as #111827 for color-style options.",
            "sort_order": "Lower numbers appear first in selectors and public filters.",
            "status": "Active values can be assigned to variants; drafts stay internal.",
        },
    )


def resolve_variant_form_schema(
    *,
    facility_profile: FacilityProfile,
    mode: str = "create",
) -> VariantFormSchema:
    offering = facility_profile.terms["offering"]
    is_edit = mode == "edit"
    return VariantFormSchema(
        page_title=f"{'Edit' if is_edit else 'Add'} {offering.lower()} variant",
        eyebrow=f"Variants / {'Edit' if is_edit else 'New'}",
        submit_label=f"{'Save' if is_edit else 'Create'} variant",
        labels={
            "sku": "Variant SKU",
            "title": "Variant title",
            "option_values": "Option values",
            "price_override": "Price override",
            "status": "Status",
            "stock_tracking_enabled": "Track stock for this variant",
        },
        help_texts={
            "sku": "Use a unique SKU across this organization.",
            "title": "Optional display title, such as Red / Medium.",
            "option_values": "Choose at most one value for each option.",
            "price_override": f"Leave blank to use the {offering.lower()} base price.",
            "status": "Active variants are ready for catalogue and checkout workflows.",
            "stock_tracking_enabled": "Turn off only for non-stocked services or digital items.",
        },
    )


class OfferingAdminForm(forms.Form):
    name = forms.CharField(max_length=180)
    code = forms.CharField(max_length=80)
    summary = forms.CharField(max_length=255, required=False)
    description = forms.CharField(required=False, widget=forms.Textarea)
    category = forms.ModelChoiceField(queryset=Category.objects.none(), required=False)
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
        self.facility = facility_profile.facility
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
        self.fields["category"].queryset = _category_queryset_for_facility(
            organization=organization,
            facility=self.facility,
        ).exclude(status__in=[RecordStatus.ARCHIVED, RecordStatus.DELETED])
        self.fields["category"].empty_label = f"No {facility_profile.terms['category'].lower()}"

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
            "category": self.cleaned_data["category"],
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

        for field_name in (
            "name",
            "code",
            "summary",
            "category",
            "base_price",
            "currency",
            "status",
        ):
            self.fields[field_name].widget.attrs.setdefault(
                "class",
                select_class if field_name in {"category", "currency", "status"} else input_class,
            )
        self.fields["description"].widget.attrs.setdefault("class", textarea_class)
        self.fields["description"].widget.attrs.setdefault("rows", 5)
        self.fields["visible_on_website"].widget.attrs.setdefault("class", checkbox_class)
        self.fields["whatsapp_inquiry_enabled"].widget.attrs.setdefault("class", checkbox_class)


class CategoryAdminForm(forms.Form):
    name = forms.CharField(max_length=160)
    slug = forms.SlugField(max_length=160, required=False)
    parent = forms.ModelChoiceField(queryset=Category.objects.none(), required=False)
    description = forms.CharField(required=False, widget=forms.Textarea)
    sort_order = forms.IntegerField(min_value=0, initial=0)
    status = forms.ChoiceField(
        choices=(
            (RecordStatus.ACTIVE, "Publish now"),
            (RecordStatus.DRAFT, "Save as draft"),
        ),
    )

    def __init__(
        self,
        *args: Any,
        organization: Organization,
        facility_profile: FacilityProfile,
        instance: Category | None = None,
        **kwargs: Any,
    ) -> None:
        self.organization = organization
        self.facility_profile = facility_profile
        self.facility = facility_profile.facility
        self.instance = instance
        self.schema = resolve_category_form_schema(
            facility_profile=facility_profile,
            mode="edit" if instance is not None else "create",
        )
        if instance is not None and not args and "initial" not in kwargs:
            kwargs["initial"] = _initial_for_category(instance)
        super().__init__(*args, **kwargs)

        self.fields["parent"].queryset = _category_parent_queryset(
            organization=organization,
            facility=self.facility,
            instance=instance,
        )
        self.fields["parent"].empty_label = (
            f"No parent {facility_profile.terms['category'].lower()}"
        )
        self.fields["status"].initial = RecordStatus.ACTIVE

        for name, label in self.schema.labels.items():
            self.fields[name].label = label
        for name, help_text in self.schema.help_texts.items():
            self.fields[name].help_text = help_text

        self._apply_widget_classes()

    def clean_slug(self) -> str:
        raw_slug = self.cleaned_data["slug"].strip()
        if not raw_slug:
            return ""
        slug = slugify(raw_slug)
        conflicts = Category.objects.filter(
            organization=self.organization,
            slug__iexact=slug,
        )
        if self.instance is not None:
            conflicts = conflicts.exclude(id=self.instance.id)
        if conflicts.exists():
            category = self.facility_profile.terms["category"].lower()
            raise forms.ValidationError(f"A {category} with this slug already exists.")
        return slug

    def clean_parent(self) -> Category | None:
        parent = self.cleaned_data["parent"]
        if parent is None:
            return None
        if parent.organization_id != self.organization.id:
            raise forms.ValidationError("Parent category must belong to this organization.")
        if self.facility is not None and parent.facility_id not in {None, self.facility.id}:
            raise forms.ValidationError("Parent category must belong to this facility.")
        if self.instance is not None and parent.id == self.instance.id:
            raise forms.ValidationError("A category cannot be its own parent.")
        return parent

    def to_service_kwargs(self) -> dict[str, Any]:
        return {
            "name": self.cleaned_data["name"].strip(),
            "slug": self.cleaned_data["slug"],
            "parent": self.cleaned_data["parent"],
            "description": self.cleaned_data["description"].strip(),
            "sort_order": self.cleaned_data["sort_order"],
            "status": self.cleaned_data["status"],
        }

    def _apply_widget_classes(self) -> None:
        input_class = "input input-bordered w-full"
        textarea_class = "textarea textarea-bordered min-h-28 w-full"
        select_class = "select select-bordered w-full"

        for field_name in ("name", "slug", "parent", "sort_order", "status"):
            self.fields[field_name].widget.attrs.setdefault(
                "class",
                select_class if field_name in {"parent", "status"} else input_class,
            )
        self.fields["description"].widget.attrs.setdefault("class", textarea_class)
        self.fields["description"].widget.attrs.setdefault("rows", 5)


class CollectionAdminForm(forms.Form):
    name = forms.CharField(max_length=160)
    slug = forms.SlugField(max_length=160, required=False)
    description = forms.CharField(required=False, widget=forms.Textarea)
    offerings = forms.ModelMultipleChoiceField(
        queryset=Offering.objects.none(),
        required=False,
    )
    status = forms.ChoiceField(
        choices=(
            (RecordStatus.ACTIVE, "Publish now"),
            (RecordStatus.DRAFT, "Save as draft"),
        ),
    )

    def __init__(
        self,
        *args: Any,
        organization: Organization,
        facility_profile: FacilityProfile,
        instance: Collection | None = None,
        **kwargs: Any,
    ) -> None:
        self.organization = organization
        self.facility_profile = facility_profile
        self.facility = facility_profile.facility
        self.instance = instance
        self.schema = resolve_collection_form_schema(
            facility_profile=facility_profile,
            mode="edit" if instance is not None else "create",
        )
        if instance is not None and not args and "initial" not in kwargs:
            kwargs["initial"] = _initial_for_collection(instance)
        super().__init__(*args, **kwargs)

        self.fields["offerings"].queryset = _offering_queryset_for_facility(
            organization=organization,
            facility=self.facility,
        ).exclude(status__in=[RecordStatus.ARCHIVED, RecordStatus.DELETED])
        self.fields["status"].initial = RecordStatus.ACTIVE

        for name, label in self.schema.labels.items():
            self.fields[name].label = label
        for name, help_text in self.schema.help_texts.items():
            self.fields[name].help_text = help_text

        self._apply_widget_classes()

    def clean_slug(self) -> str:
        raw_slug = self.cleaned_data["slug"].strip()
        if not raw_slug:
            return ""
        slug = slugify(raw_slug)
        conflicts = Collection.objects.filter(
            organization=self.organization,
            slug__iexact=slug,
        )
        if self.instance is not None:
            conflicts = conflicts.exclude(id=self.instance.id)
        if conflicts.exists():
            raise forms.ValidationError("A collection with this slug already exists.")
        return slug

    def to_service_kwargs(self) -> dict[str, Any]:
        return {
            "name": self.cleaned_data["name"].strip(),
            "slug": self.cleaned_data["slug"],
            "description": self.cleaned_data["description"].strip(),
            "offerings": list(self.cleaned_data["offerings"]),
            "status": self.cleaned_data["status"],
        }

    def _apply_widget_classes(self) -> None:
        input_class = "input input-bordered w-full"
        textarea_class = "textarea textarea-bordered min-h-28 w-full"
        select_class = "select select-bordered w-full"
        multi_select_class = "select select-bordered min-h-36 w-full"

        for field_name in ("name", "slug", "status"):
            self.fields[field_name].widget.attrs.setdefault(
                "class",
                select_class if field_name == "status" else input_class,
            )
        self.fields["description"].widget.attrs.setdefault("class", textarea_class)
        self.fields["description"].widget.attrs.setdefault("rows", 5)
        self.fields["offerings"].widget.attrs.setdefault("class", multi_select_class)
        self.fields["offerings"].widget.attrs.setdefault("size", 8)


class OptionDefinitionAdminForm(forms.Form):
    name = forms.CharField(max_length=80)
    code = forms.CharField(max_length=80)
    sort_order = forms.IntegerField(min_value=0, initial=0)
    status = forms.ChoiceField(
        choices=(
            (RecordStatus.ACTIVE, "Active"),
            (RecordStatus.DRAFT, "Draft"),
        ),
    )

    def __init__(
        self,
        *args: Any,
        organization: Organization,
        facility_profile: FacilityProfile,
        instance: OptionDefinition | None = None,
        **kwargs: Any,
    ) -> None:
        self.organization = organization
        self.facility_profile = facility_profile
        self.facility = facility_profile.facility
        self.instance = instance
        self.schema = resolve_option_form_schema(
            mode="edit" if instance is not None else "create"
        )
        if instance is not None and not args and "initial" not in kwargs:
            kwargs["initial"] = _initial_for_option(instance)
        super().__init__(*args, **kwargs)

        self.fields["status"].initial = RecordStatus.ACTIVE
        for name, label in self.schema.labels.items():
            self.fields[name].label = label
        for name, help_text in self.schema.help_texts.items():
            self.fields[name].help_text = help_text
        self._apply_widget_classes()

    def clean_code(self) -> str:
        code = slugify(self.cleaned_data["code"].strip()).lower()
        if not code or not OPTION_CODE_PATTERN.fullmatch(code):
            raise forms.ValidationError(
                "Use lowercase letters, numbers, and hyphens, starting with a letter or number."
            )
        conflicts = OptionDefinition.objects.filter(
            organization=self.organization,
            code__iexact=code,
        )
        if self.instance is not None:
            conflicts = conflicts.exclude(id=self.instance.id)
        if conflicts.exists():
            raise forms.ValidationError("An option with this code already exists.")
        return code

    def to_service_kwargs(self) -> dict[str, Any]:
        return {
            "name": self.cleaned_data["name"].strip(),
            "code": self.cleaned_data["code"],
            "sort_order": self.cleaned_data["sort_order"],
            "status": self.cleaned_data["status"],
        }

    def _apply_widget_classes(self) -> None:
        input_class = "input input-bordered w-full"
        select_class = "select select-bordered w-full"
        for field_name in ("name", "code", "sort_order", "status"):
            self.fields[field_name].widget.attrs.setdefault(
                "class",
                select_class if field_name == "status" else input_class,
            )


class OptionValueAdminForm(forms.Form):
    label = forms.CharField(max_length=80)
    value = forms.CharField(max_length=80)
    color_hex = forms.CharField(max_length=7, required=False)
    sort_order = forms.IntegerField(min_value=0, initial=0)
    status = forms.ChoiceField(
        choices=(
            (RecordStatus.ACTIVE, "Active"),
            (RecordStatus.DRAFT, "Draft"),
        ),
    )

    def __init__(
        self,
        *args: Any,
        organization: Organization,
        facility_profile: FacilityProfile,
        option: OptionDefinition,
        instance: OptionValue | None = None,
        **kwargs: Any,
    ) -> None:
        self.organization = organization
        self.facility_profile = facility_profile
        self.facility = facility_profile.facility
        self.option = option
        self.instance = instance
        self.schema = resolve_option_value_form_schema(
            option=option,
            mode="edit" if instance is not None else "create",
        )
        if instance is not None and not args and "initial" not in kwargs:
            kwargs["initial"] = _initial_for_option_value(instance)
        super().__init__(*args, **kwargs)

        self.fields["status"].initial = RecordStatus.ACTIVE
        for name, label in self.schema.labels.items():
            self.fields[name].label = label
        for name, help_text in self.schema.help_texts.items():
            self.fields[name].help_text = help_text
        self._apply_widget_classes()

    def clean_value(self) -> str:
        value = slugify(self.cleaned_data["value"].strip()).lower()
        if not value or not OPTION_CODE_PATTERN.fullmatch(value):
            raise forms.ValidationError(
                "Use lowercase letters, numbers, and hyphens, starting with a letter or number."
            )
        conflicts = OptionValue.objects.filter(
            organization=self.organization,
            option=self.option,
            value__iexact=value,
        )
        if self.instance is not None:
            conflicts = conflicts.exclude(id=self.instance.id)
        if conflicts.exists():
            raise forms.ValidationError("This option already has that value.")
        return value

    def clean_color_hex(self) -> str:
        color_hex = self.cleaned_data["color_hex"].strip()
        if color_hex and not COLOR_HEX_PATTERN.fullmatch(color_hex):
            raise forms.ValidationError("Use a valid hex color such as #111827.")
        return color_hex.upper()

    def to_service_kwargs(self) -> dict[str, Any]:
        return {
            "label": self.cleaned_data["label"].strip(),
            "value": self.cleaned_data["value"],
            "color_hex": self.cleaned_data["color_hex"],
            "sort_order": self.cleaned_data["sort_order"],
            "status": self.cleaned_data["status"],
        }

    def _apply_widget_classes(self) -> None:
        input_class = "input input-bordered w-full"
        select_class = "select select-bordered w-full"
        for field_name in ("label", "value", "color_hex", "sort_order", "status"):
            self.fields[field_name].widget.attrs.setdefault(
                "class",
                select_class if field_name == "status" else input_class,
            )


class OfferingVariantAdminForm(forms.Form):
    sku = forms.CharField(max_length=80)
    title = forms.CharField(max_length=180, required=False)
    option_values = forms.ModelMultipleChoiceField(
        queryset=OptionValue.objects.none(),
        required=False,
    )
    price_override = forms.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal("0.00"),
        required=False,
    )
    status = forms.ChoiceField(
        choices=(
            (RecordStatus.ACTIVE, "Active"),
            (RecordStatus.DRAFT, "Draft"),
        ),
    )
    stock_tracking_enabled = forms.BooleanField(required=False, initial=True)

    def __init__(
        self,
        *args: Any,
        organization: Organization,
        facility_profile: FacilityProfile,
        offering: Offering,
        instance: OfferingVariant | None = None,
        **kwargs: Any,
    ) -> None:
        self.organization = organization
        self.facility_profile = facility_profile
        self.facility = offering.facility
        self.offering = offering
        self.instance = instance
        self.schema = resolve_variant_form_schema(
            facility_profile=facility_profile,
            mode="edit" if instance is not None else "create",
        )
        if instance is not None and not args and "initial" not in kwargs:
            kwargs["initial"] = _initial_for_variant(instance)
        super().__init__(*args, **kwargs)

        self.fields["option_values"].queryset = _option_value_queryset_for_facility(
            organization=organization,
            facility=self.facility,
        ).exclude(status__in=[RecordStatus.ARCHIVED, RecordStatus.DELETED])
        self.fields["status"].initial = RecordStatus.ACTIVE
        for name, label in self.schema.labels.items():
            self.fields[name].label = label
        for name, help_text in self.schema.help_texts.items():
            self.fields[name].help_text = help_text
        self._apply_widget_classes()

    def clean_sku(self) -> str:
        sku = self.cleaned_data["sku"].strip().upper()
        if not OFFERING_CODE_PATTERN.fullmatch(sku):
            raise forms.ValidationError(
                "Use letters, numbers, dots, hyphens, or underscores, "
                "starting with a letter or number."
            )
        conflicts = OfferingVariant.objects.filter(
            organization=self.organization,
            sku__iexact=sku,
        )
        if self.instance is not None:
            conflicts = conflicts.exclude(id=self.instance.id)
        if conflicts.exists():
            raise forms.ValidationError("A variant with this SKU already exists.")
        return sku

    def clean_option_values(self):
        option_values = list(self.cleaned_data["option_values"])
        option_ids = set()
        for value in option_values:
            if value.option_id in option_ids:
                raise forms.ValidationError("Choose only one value for each option.")
            option_ids.add(value.option_id)
        return option_values

    def to_service_kwargs(self) -> dict[str, Any]:
        return {
            "sku": self.cleaned_data["sku"],
            "title": self.cleaned_data["title"].strip(),
            "option_values": list(self.cleaned_data["option_values"]),
            "price_override": self.cleaned_data["price_override"],
            "status": self.cleaned_data["status"],
            "stock_tracking_enabled": self.cleaned_data["stock_tracking_enabled"],
        }

    def _apply_widget_classes(self) -> None:
        input_class = "input input-bordered w-full"
        select_class = "select select-bordered w-full"
        multi_select_class = "select select-bordered min-h-36 w-full"
        checkbox_class = "checkbox checkbox-primary"
        for field_name in ("sku", "title", "price_override", "status"):
            self.fields[field_name].widget.attrs.setdefault(
                "class",
                select_class if field_name == "status" else input_class,
            )
        self.fields["option_values"].widget.attrs.setdefault("class", multi_select_class)
        self.fields["option_values"].widget.attrs.setdefault("size", 8)
        self.fields["stock_tracking_enabled"].widget.attrs.setdefault("class", checkbox_class)


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
        "category": offering.category,
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


def _initial_for_category(category: Category) -> dict[str, Any]:
    return {
        "name": category.name,
        "slug": category.slug,
        "parent": category.parent,
        "description": category.description,
        "sort_order": category.sort_order,
        "status": category.status,
    }


def _initial_for_collection(collection: Collection) -> dict[str, Any]:
    return {
        "name": collection.name,
        "slug": collection.slug,
        "description": collection.description,
        "offerings": list(collection.offerings.values_list("id", flat=True)),
        "status": collection.status,
    }


def _initial_for_option(option: OptionDefinition) -> dict[str, Any]:
    return {
        "name": option.name,
        "code": option.code,
        "sort_order": option.sort_order,
        "status": option.status,
    }


def _initial_for_option_value(option_value: OptionValue) -> dict[str, Any]:
    return {
        "label": option_value.label,
        "value": option_value.value,
        "color_hex": option_value.color_hex,
        "sort_order": option_value.sort_order,
        "status": option_value.status,
    }


def _initial_for_variant(variant: OfferingVariant) -> dict[str, Any]:
    return {
        "sku": variant.sku,
        "title": variant.title,
        "option_values": list(variant.option_values.values_list("id", flat=True)),
        "price_override": variant.price_override,
        "status": variant.status,
        "stock_tracking_enabled": variant.stock_tracking_enabled,
    }


def _category_queryset_for_facility(
    *,
    organization: Organization,
    facility: Facility | None,
):
    queryset = Category.objects.filter(organization=organization)
    if facility is None:
        return queryset.filter(facility__isnull=True)
    return queryset.filter(Q(facility__isnull=True) | Q(facility=facility))


def _category_parent_queryset(
    *,
    organization: Organization,
    facility: Facility | None,
    instance: Category | None,
):
    queryset = _category_queryset_for_facility(
        organization=organization,
        facility=facility,
    ).exclude(status__in=[RecordStatus.ARCHIVED, RecordStatus.DELETED])
    if instance is None:
        return queryset.order_by("sort_order", "name")
    excluded_ids = {instance.id, *_category_descendant_ids(instance)}
    return queryset.exclude(id__in=excluded_ids).order_by("sort_order", "name")


def _offering_queryset_for_facility(
    *,
    organization: Organization,
    facility: Facility | None,
):
    queryset = Offering.objects.filter(organization=organization)
    if facility is None:
        return queryset.filter(facility__isnull=True).order_by("name")
    return queryset.filter(Q(facility__isnull=True) | Q(facility=facility)).order_by("name")


def _option_value_queryset_for_facility(
    *,
    organization: Organization,
    facility: Facility | None,
):
    queryset = OptionValue.objects.filter(organization=organization).select_related("option")
    if facility is None:
        return queryset.filter(
            facility__isnull=True,
            option__facility__isnull=True,
            option__status=RecordStatus.ACTIVE,
        ).order_by("option__sort_order", "sort_order", "label")
    return queryset.filter(
        Q(facility__isnull=True) | Q(facility=facility),
        Q(option__facility__isnull=True) | Q(option__facility=facility),
        option__status=RecordStatus.ACTIVE,
    ).order_by("option__sort_order", "sort_order", "label")


def _category_descendant_ids(category: Category) -> set[Any]:
    descendants: set[Any] = set()
    frontier = [category.id]
    while frontier:
        child_ids = list(
            Category.objects.filter(parent_id__in=frontier).values_list("id", flat=True)
        )
        new_child_ids = [child_id for child_id in child_ids if child_id not in descendants]
        descendants.update(new_child_ids)
        frontier = new_child_ids
    return descendants
