# -*- coding: utf-8 -*-
# Copyright (c) 2019, Bloomstack, Inc and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe
from bloomstack_core.compliance.item import create_item, update_item
from frappe import _
from frappe.model.document import Document


class ComplianceItem(Document):
	def validate(self):
		self.validate_existing_metrc_item()
		self.sync_metrc_item()

	def validate_existing_metrc_item(self):
		if self.is_new() and frappe.db.exists("Compliance Item", self.item_code):
			frappe.throw(_("A Compliance Item already exists for {}".format(self.item_code)))

	def sync_metrc_item(self):
		item = frappe.get_doc("Item", self.item_code)

		# Merge Item and Compliance Item data
		item.update(self.as_dict())

		if self.is_new():
			metrc_id = create_item(item)

			if metrc_id:
				self.metrc_id = metrc_id
				frappe.msgprint(_("{} was successfully created in METRC (ID number: {}).".format(item.item_name, self.metrc_id)))
			else:
				frappe.msgprint(_("{} was successfully created in METRC.".format(item.item_name)))
		else:
			update_item(item)
			frappe.msgprint(_("{} was successfully updated in METRC.".format(item.item_name)))


def metrc_item_category_query(doctype, txt, searchfield, start, page_len, filters):
	metrc_uom = filters.get("metrc_uom")
	quantity_type = frappe.db.get_value("Compliance UOM", metrc_uom, "quantity_type")

	return frappe.get_all("Compliance Item Category", filters={"quantity_type": quantity_type}, as_list=1)


def metrc_uom_query(doctype, txt, searchfield, start, page_len, filters):
	metrc_item_category = filters.get("metrc_item_category")
	quantity_type = frappe.db.get_value("Compliance Item Category", metrc_item_category, "quantity_type")

	return frappe.get_all("Compliance UOM", filters={"quantity_type": quantity_type}, as_list=1)


def metrc_unit_uom_query(doctype, txt, searchfield, start, page_len, filters):
	metrc_item_category = filters.get("metrc_item_category")
	mandatory_unit = frappe.db.get_value("Compliance Item Category", metrc_item_category, "mandatory_unit")

	quantity_type = None
	if mandatory_unit == "Volume":
		quantity_type = "VolumeBased"
	elif mandatory_unit == "Weight":
		quantity_type = "WeightBased"

	return frappe.get_all("Compliance UOM", filters={"quantity_type": quantity_type}, as_list=1)