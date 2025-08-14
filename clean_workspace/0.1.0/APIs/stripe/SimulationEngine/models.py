from datetime import datetime
from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, EmailStr, field_validator, PositiveInt

VALID_SUBSCRIPTION_STATUSES = {
    'active',
    'past_due',
    'unpaid',
    'canceled',
    'incomplete',
    'incomplete_expired',
    'trialing',
    'all'  # Valid for filtering, but not a valid subscription status
}

# Valid subscription statuses for the model (excluding 'all' which is only for filtering)
SUBSCRIPTION_STATUS_LITERALS = Literal[
    'active',
    'past_due', 
    'unpaid',
    'canceled',
    'incomplete',
    'incomplete_expired',
    'trialing'
]

# Valid invoice statuses
INVOICE_STATUS_LITERALS = Literal[
    'draft',
    'open', 
    'paid',
    'void',
    'uncollectible'
]

# Valid refund statuses
REFUND_STATUS_LITERALS = Literal[
    'succeeded',
    'pending',
    'failed',
    'canceled'
]

# Valid payment intent statuses
PAYMENT_INTENT_STATUS_LITERALS = Literal[
    'requires_payment_method',
    'requires_confirmation',
    'requires_action',
    'processing',
    'requires_capture',
    'canceled',
    'succeeded'
]

# Valid dispute statuses
DISPUTE_STATUS_LITERALS = Literal[
    'warning_needs_response',
    'under_review',
    'won',
    'lost',
    'closed'
]

# Valid coupon durations
COUPON_DURATION_LITERALS = Literal[
    'once',
    'repeating',
    'forever'
]

# Utility to generate unique IDs and timestamps for simulation
def generate_id(prefix: str) -> str:
    return f"{prefix}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"

def get_current_timestamp() -> int:
    return int(datetime.now().timestamp())

_SUPPORTED_CURRENCIES_FOR_MODEL = {"usd", "eur", "gbp", "jpy", "cad", "aud"}

class Customer(BaseModel):
    id: str = Field(default_factory=lambda: generate_id("cus"))
    object: str = "customer"
    name: str
    email: Optional[EmailStr] = None
    created: int = Field(default_factory=get_current_timestamp)
    livemode: bool = False
    metadata: Optional[Dict[str, str]] = None

class Product(BaseModel):
    id: str = Field(default_factory=lambda: generate_id("prod"))
    object: str = "product"
    name: str
    description: Optional[str] = None
    active: bool = True
    created: int = Field(default_factory=get_current_timestamp)
    updated: int = Field(default_factory=get_current_timestamp)
    livemode: bool = False
    metadata: Optional[Dict[str, str]] = None

class PriceCustomUnitAmount(BaseModel):
    maximum: Optional[int] = None
    minimum: Optional[int] = None
    preset: Optional[int] = None

class PriceRecurring(BaseModel):
    interval: str # Can be `day`, `week`, `month`, or `year`
    interval_count: int
    trial_period_days: Optional[int] = None
    usage_type: str # Can be `metered` or `licensed`

class PriceTier(BaseModel):
    flat_amount: Optional[int] = None
    flat_amount_decimal: Optional[str] = None
    unit_amount: Optional[int] = None
    unit_amount_decimal: Optional[str] = None
    up_to: Optional[int] = None

class PriceTransformQuantity(BaseModel):
    divide_by: int
    round: Literal["up", "down"]

class Price(BaseModel):
    id: str = Field(default_factory=lambda: generate_id("price"))
    object: str = "price"
    active: bool = True
    product: str # Product ID
    unit_amount: Optional[int] = None # Made Optional as tiered prices might have unit_amount=0 or None at top level
    currency: str
    type: str = "one_time"  # Can be 'one_time' or 'recurring'
    recurring: Optional[PriceRecurring] = None
    livemode: bool = False
    metadata: Optional[Dict[str, str]] = None
    billing_scheme: str = "per_unit" #Can be 'per_unit' or 'tiered'
    created: int = Field(default_factory=get_current_timestamp)
    custom_unit_amount: Optional[PriceCustomUnitAmount] = None
    lookup_key: Optional[str] = None
    nickname: Optional[str] = None
    tax_behavior: Optional[str] = None
    tiers: Optional[List[PriceTier]] = None
    tiers_mode: Optional[str] = None
    transform_quantity: Optional[PriceTransformQuantity] = None
    unit_amount_decimal: Optional[str] = None

    @field_validator("product")
    @classmethod
    def validate_product_rules(cls, v: str) -> str:
        """Validate product ID: must be non-empty and start with 'prod_'."""
        if not v.strip():
            raise ValueError("Product ID must be a non-empty string.")
        if not v.startswith("prod_"):
            raise ValueError(f"Product ID '{v}' is malformed. Expected format 'prod_<identifier>'.")
        return v  

    @field_validator("unit_amount")
    @classmethod
    def validate_unit_amount_rules(cls, v: Optional[int]) -> Optional[int]:
        """Validate unit_amount: must be a non-negative integer if provided."""
        if v is not None:
            if v < 0:
                raise ValueError("Unit amount must be a non-negative integer representing cents.")
        return v 

    @field_validator("currency")
    @classmethod
    def validate_and_normalize_currency(cls, v: str) -> str:
        """Validate currency: must be a 3-letter ISO code from supported list, normalized to lowercase."""
        processed_v = v.lower().strip()
        if not (len(processed_v) == 3 and processed_v.isalpha()):
            raise ValueError(f"Currency '{v}' must be a 3-letter ISO code (e.g., usd, eur).")
        if processed_v not in _SUPPORTED_CURRENCIES_FOR_MODEL:
            supported_str = ", ".join(sorted(list(_SUPPORTED_CURRENCIES_FOR_MODEL)))
            raise ValueError(f"Unsupported currency: '{v}'. Supported currencies are: {supported_str}.")
        return processed_v

class PriceList(BaseModel):
    object: Literal["list"]
    data: List[Price]
    has_more: bool

class PaymentLinkLineItemPrice(BaseModel):
    id: str
    product: str # Product ID

class PaymentLinkLineItem(BaseModel):
    id: str = Field(default_factory=lambda: generate_id("sli")) # Simulated line item ID
    price: PaymentLinkLineItemPrice
    quantity: int

class PaymentLinkLineItems(BaseModel):
    object: str = "list"
    data: List[PaymentLinkLineItem]
    has_more: bool = False

class PaymentLinkAfterCompletionRedirect(BaseModel):
    url: str

class PaymentLinkAfterCompletion(BaseModel):
    type: str
    redirect: Optional[PaymentLinkAfterCompletionRedirect] = None

class PaymentLink(BaseModel):
    id: str = Field(default_factory=lambda: generate_id("pl"))
    object: str = "payment_link"
    active: bool = True
    livemode: bool = False
    metadata: Optional[Dict[str, str]] = None
    line_items: PaymentLinkLineItems
    after_completion: PaymentLinkAfterCompletion


class InvoiceLineItemPrice(BaseModel):
    id: str
    product: str

class InvoiceLineItem(BaseModel):
    id: str = Field(default_factory=lambda: generate_id("il_")) # Simulated line item ID
    amount: int
    description: Optional[str] = None
    price: Optional[InvoiceLineItemPrice] = None
    quantity: Optional[int] = None

class InvoiceLines(BaseModel):
    object: str = "list"
    data: List[InvoiceLineItem]
    has_more: bool = False

class Invoice(BaseModel):
    id: str = Field(default_factory=lambda: generate_id("inv"))
    object: str = "invoice"
    customer: str # Customer ID
    status: INVOICE_STATUS_LITERALS = "draft"
    total: int = 0
    amount_due: int = 0
    currency: str = "usd" # Default currency
    created: int = Field(default_factory=get_current_timestamp)
    due_date: Optional[int] = None
    livemode: bool = False
    metadata: Optional[Dict[str, str]] = None
    lines: InvoiceLines = Field(default_factory=lambda: InvoiceLines(data=[]))


class InvoiceItemPrice(BaseModel):
    id: str
    product: str
    unit_amount: Optional[int] = None
    currency: str

class InvoiceItem(BaseModel):
    id: str = Field(default_factory=lambda: generate_id("ii"))
    object: str = "invoiceitem"
    customer: str # Customer ID
    invoice: Optional[str] = None # Invoice ID
    price: InvoiceItemPrice
    amount: int
    currency: str
    quantity: int
    livemode: bool = False
    metadata: Optional[Dict[str, str]] = None


class BalanceAmountBySourceType(BaseModel):
    amount: int
    currency: str
    source_types: Optional[Dict[str, int]] = None

class Balance(BaseModel):
    object: str = "balance"
    available: List[BalanceAmountBySourceType] = Field(default_factory=list)
    pending: List[BalanceAmountBySourceType] = Field(default_factory=list)
    livemode: bool = False

class Refund(BaseModel):
    id: str = Field(default_factory=lambda: generate_id("re"))
    object: str = "refund"
    payment_intent: str # PaymentIntent ID
    amount: int
    currency: str = "usd"
    status: REFUND_STATUS_LITERALS = "succeeded"
    reason: Optional[str] = None
    created: int = Field(default_factory=get_current_timestamp)
    metadata: Optional[Dict[str, str]] = None

class PaymentIntent(BaseModel):
    id: str = Field(default_factory=lambda: generate_id("pi"))
    object: str = "payment_intent"
    amount: int
    currency: str
    customer: Optional[str] = None # Customer ID
    status: PAYMENT_INTENT_STATUS_LITERALS = "requires_payment_method"
    created: int = Field(default_factory=get_current_timestamp)
    livemode: bool = False
    metadata: Optional[Dict[str, str]] = None

class ListPaymentIntentsResponse(BaseModel):
    """
    A dictionary representing the API response for listing payment intents.
    """
    object: str = Field(default="list", description="String representing the object's type, typically \"list\".")
    data: List['PaymentIntent'] # Referencing PaymentIntent, assumed to be imported
    has_more: bool = Field(description="True if there are more payment intents to retrieve, false otherwise.")

class SubscriptionItemPrice(BaseModel):
    id: str
    product: str
    active: bool = True
    currency: str
    unit_amount: Optional[int] = None
    type: str
    recurring: Optional[PriceRecurring] = None

class SubscriptionItem(BaseModel):
    id: str = Field(default_factory=lambda: generate_id("si"))
    object: str = "subscription_item"
    price: SubscriptionItemPrice
    quantity: int
    created: int = Field(default_factory=get_current_timestamp)
    metadata: Optional[Dict[str, str]] = None

class SubscriptionItems(BaseModel):
    object: str = "list"
    data: List[SubscriptionItem]
    has_more: bool = False

class SubscriptionDiscountCoupon(BaseModel):
    id: str
    name: Optional[str] = None
    valid: bool

class SubscriptionDiscount(BaseModel):
    id: str
    coupon: SubscriptionDiscountCoupon

class Subscription(BaseModel):
    id: str = Field(default_factory=lambda: generate_id("sub"))
    object: str = "subscription"
    customer: str # Customer ID
    status: SUBSCRIPTION_STATUS_LITERALS = "active"
    current_period_start: int = Field(default_factory=get_current_timestamp)
    current_period_end: int = Field(default_factory=get_current_timestamp)
    created: int = Field(default_factory=get_current_timestamp)
    items: SubscriptionItems = Field(default_factory=lambda: SubscriptionItems(data=[]))
    livemode: bool = False
    metadata: Optional[Dict[str, str]] = None
    cancel_at_period_end: bool = False
    canceled_at: Optional[int] = None
    start_date: int = Field(default_factory=get_current_timestamp)
    ended_at: Optional[int] = None
    trial_start: Optional[int] = None
    trial_end: Optional[int] = None
    latest_invoice: Optional[str] = None # Invoice ID
    default_payment_method: Optional[str] = None
    discount: Optional[SubscriptionDiscount] = None


class Coupon(BaseModel):
    id: str = Field(default_factory=lambda: generate_id("cou"))
    object: str = "coupon"
    name: Optional[str] = None
    percent_off: Optional[float] = None
    amount_off: Optional[int] = None
    currency: Optional[str] = None
    duration: COUPON_DURATION_LITERALS = "once"
    duration_in_months: Optional[int] = None
    livemode: bool = False
    valid: bool = True
    metadata: Optional[Dict[str, str]] = None

class CouponListResponse(BaseModel):
    """
    A dictionary containing the list of coupons and related information.
    """
    object: str = Literal["list"]
    data: List['Coupon']
    has_more: bool = Field(description="True if there are more coupons to retrieve.")

class DisputeEvidence(BaseModel):
    cancellation_policy_disclosure: Optional[str] = None
    cancellation_rebuttal: Optional[str] = None
    duplicate_charge_explanation: Optional[str] = None
    uncategorized_text: Optional[str] = None

class Dispute(BaseModel):
    id: str = Field(default_factory=lambda: generate_id("dp"))
    object: str = "dispute"
    amount: int
    currency: str
    status: DISPUTE_STATUS_LITERALS = "warning_needs_response"
    reason: str
    charge: str # Charge ID
    payment_intent: Optional[str] = None # PaymentIntent ID
    created: int = Field(default_factory=get_current_timestamp)
    evidence: DisputeEvidence = Field(default_factory=DisputeEvidence)
    is_charge_refundable: bool = False
    livemode: bool = False
    metadata: Optional[Dict[str, str]] = None


class StripeDB(BaseModel):
    customers: Dict[str, Customer] = Field(default_factory=dict)
    products: Dict[str, Product] = Field(default_factory=dict)
    prices: Dict[str, Price] = Field(default_factory=dict)
    payment_links: Dict[str, PaymentLink] = Field(default_factory=dict)
    invoices: Dict[str, Invoice] = Field(default_factory=dict)
    invoice_items: Dict[str, InvoiceItem] = Field(default_factory=dict)
    balance: Balance = Field(default_factory=Balance)
    refunds: Dict[str, Refund] = Field(default_factory=dict)
    payment_intents: Dict[str, PaymentIntent] = Field(default_factory=dict)
    subscriptions: Dict[str, Subscription] = Field(default_factory=dict)
    coupons: Dict[str, Coupon] = Field(default_factory=dict)
    disputes: Dict[str, Dispute] = Field(default_factory=dict)


class ListSubscriptionsResponseItem(BaseModel):
    id: str
    price: InvoiceLineItemPrice
    quantity: int

class ListSubscriptionsResponse(BaseModel):
    object: str = Field(default="list", description="String representing the object's type, typically \"list\".")
    data: List[Subscription]
    has_more: bool

class UpdateSubscriptionItem(BaseModel):
    id: str = None
    price: str = None
    quantity: PositiveInt = None
    deleted: bool = None
