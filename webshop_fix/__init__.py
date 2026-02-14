__version__ = "0.0.1"


def patch_webshop_cart():
	"""Monkey patch webshop cart module to fix receivable account selection."""
	try:
		import webshop.webshop.shopping_cart.cart as cart_module
		from webshop_fix.overrides.cart import get_debtors_account

		# Override the get_debtors_account function
		cart_module.get_debtors_account = get_debtors_account
	except ImportError:
		# Webshop app might not be installed
		pass


# Apply patch when app is imported
patch_webshop_cart()
