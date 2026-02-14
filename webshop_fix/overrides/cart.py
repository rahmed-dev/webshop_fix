# -*- coding: utf-8 -*-
# Copyright (c) 2026, globcom and contributors
# License: MIT

"""
Override for webshop.webshop.shopping_cart.cart module.

Fixes the issue where multiple receivable accounts exist and the wrong one
is selected for customer creation in webshop.
"""

import frappe
from frappe import _
from erpnext.accounts.utils import get_account_name


def get_debtors_account(cart_settings):
	"""Get the receivable account for webshop customer creation.

	First checks if a specific 'Webshop Receivable Account' is configured
	in Webshop Settings. If set, uses that account. Otherwise, falls back
	to the original logic of auto-detecting based on payment gateway currency.

	Args:
		cart_settings (Document): Webshop Settings document

	Returns:
		str: Account name for receivable account

	Raises:
		frappe.ValidationError: If payment gateway account is not set
	"""
	# Check if custom field is set in Webshop Settings
	webshop_receivable_account = cart_settings.get("webshop_receivable_account")

	if webshop_receivable_account:
		# Validate that the account exists and is a receivable account
		account_type = frappe.db.get_value(
			"Account",
			webshop_receivable_account,
			["account_type", "company"],
			as_dict=True
		)

		if not account_type:
			frappe.throw(
				_("Webshop Receivable Account {0} does not exist").format(webshop_receivable_account)
			)

		if account_type.account_type != "Receivable":
			frappe.throw(
				_("Account {0} must be a Receivable type account").format(webshop_receivable_account)
			)

		if account_type.company != cart_settings.company:
			frappe.throw(
				_("Account {0} must belong to company {1}").format(
					webshop_receivable_account, cart_settings.company
				)
			)

		return webshop_receivable_account

	# Fall back to original logic if custom field is not set
	if not cart_settings.payment_gateway_account:
		frappe.throw(_("Payment Gateway Account not set"), _("Mandatory"))

	payment_gateway_account_currency = frappe.get_doc(
		"Payment Gateway Account", cart_settings.payment_gateway_account
	).currency

	account_name = _("Debtors ({0})").format(payment_gateway_account_currency)

	debtors_account_name = get_account_name(
		"Receivable",
		"Asset",
		is_group=0,
		account_currency=payment_gateway_account_currency,
		company=cart_settings.company,
	)

	if not debtors_account_name:
		debtors_account = frappe.get_doc(
			{
				"doctype": "Account",
				"account_type": "Receivable",
				"root_type": "Asset",
				"is_group": 0,
				"parent_account": get_account_name(
					root_type="Asset", is_group=1, company=cart_settings.company
				),
				"account_name": account_name,
				"currency": payment_gateway_account_currency,
			}
		).insert(ignore_permissions=True)

		return debtors_account.name

	else:
		return debtors_account_name
