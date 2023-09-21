from django.db import models
from django.utils.translation import gettext_lazy as _

class TermType(models.IntegerChoices):
    SUBSCRIPTION = 100, _("Subscription")
    MONTHLY_SUBSCRIPTION = 101, _("Monthly Subscription")
    QUARTERLY_SUBSCRIPTION = 103, _("Quarterly Subscription")
    SEMIANNUAL_SUBSCRIPTION = 106, _("Semi-Annual Subscription")
    ANNUAL_SUBSCRIPTION = 112, _("Annual Subscription")
    PERPETUAL = 200, _("Perpetual")
    ONE_TIME_USE = 220, _("One-Time Use")


class PurchaseStatus(models.IntegerChoices):
    QUEUED = 1, _("Queued")
    ACTIVE = 2, _("Active")
    AUTHORIZED = 10, _("Authorized")
    CAPTURED = 15, _("Captured")
    SETTLED = 20, _("Settled")
    CANCELED = 30, _("Canceled")
    REFUNDED = 35, _("Refunded")
    DECLINED = 40, _("Declined")
    ERROR = 45, _("Error")
    VOID = 50, _('Void')

class PaymentTypes(models.IntegerChoices):
    CREDIT_CARD = 10, _('Credit Card')
    BANK_ACCOUNT = 20, _('Bank Account')
    PAY_PAL = 30, _('Pay Pal')
    MOBILE = 40, _('Mobile')


class SubscriptionStatus(models.IntegerChoices):
    PAUSED = 10, _('Pause')
    ACTIVE = 20, _('Active')
    CANCELED = 30, _('Canceled')
    SUSPENDED = 40, _('Suspended')
    EXPIRED = 50, _('Expired')


from django.contrib.sites.managers import CurrentSiteManager

##################
# MODELMANAGERS
##################
class ActiveManager(models.Manager):
    """
    This Model Manger returns offers that are available
    """
    def get_queryset(self):
        return super().get_queryset().filter(available=True)


class ActiveCurrentSiteManager(CurrentSiteManager):
    """
    This Model Manager return offers per site that are available
    """
    def get_queryset(self):
        return super().get_queryset().filter(available=True)


class SoftDeleteManager(models.Manager):

    def get_queryset(self):
        return super().get_queryset().filter(deleted=False)


class CurrentSiteSoftDeleteManager(CurrentSiteManager):

    def get_queryset(self):
        return super().get_queryset().filter(deleted=False)
    

##################
# BASE MODELS
##################

class CreateUpdateModelBase(models.Model):
    '''
    This is a shared models base that provides created & updated timestamp fields
    '''
    created = models.DateTimeField("date created", auto_now_add=True)
    updated = models.DateTimeField("last updated", auto_now=True)

    class Meta:
        abstract = True

#####################
# TAX CLASSIFIER
#####################
class TaxClassifier(models.Model):
    '''
    This for things like "Digital Goods", "Furniture" or "Food" which may or
    may not be taxable depending on the location.  These are determined by the
    manager of all sites.
    These classifiers will retain certian provider specific codes that are used
    to help calculate the tax liability in the sale.
    '''
    name = models.CharField(_("Name"), max_length=80, blank=True)
    taxable = models.BooleanField(_("Taxable"))
    # info = models.ManyToManyField("vendor.TaxInfo")                 # Which taxes is this subject to and where.  This is for a more complex tax setup

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Product Classifier"
        verbose_name_plural = "Product Classifiers"