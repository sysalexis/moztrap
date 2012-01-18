# Case Conductor is a Test Case Management system.
# Copyright (C) 2011-12 Mozilla
#
# This file is part of Case Conductor.
#
# Case Conductor is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Case Conductor is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Case Conductor.  If not, see <http://www.gnu.org/licenses/>.
"""
Tests for Case Conductor form utilities.

"""
from django.utils.unittest import TestCase

from django import forms

from .. import factories as F

from cc.core import ccforms, models



class PersonForm(ccforms.NonFieldErrorsClassFormMixin, forms.Form):
    name = forms.CharField()
    age = forms.IntegerField()

    def clean(self):
        if (self.cleaned_data.get("name") == "Shakespeare" and
            self.cleaned_data.get("age", 0) < 400):
            raise forms.ValidationError("Too young to be Shakespeare.")



class TestNonFieldErrorsClassFormMixin(TestCase):
    def test_non_field_errorlist(self):
        form = PersonForm({"name": "Shakespeare", "age": "25"})

        nfe = form.non_field_errors()

        self.assertTrue('class="errorlist nonfield"' in unicode(nfe))


    def test_field_errorlist(self):
        form = PersonForm({"name": "Joe"})

        fe = unicode(form["age"].errors)

        self.assertTrue('class="' in fe)
        self.assertFalse("nonfield" in fe)


    def test_no_nonfield_errors(self):
        form = PersonForm({"name": "Joe", "age": "25"})

        self.assertEqual(unicode(form.non_field_errors()), u"")



class BareTextareaTest(TestCase):
    def test_no_attrs(self):
        self.assertEqual(ccforms.BareTextarea().attrs, {})



class ProductVersionForm(forms.Form):
    product = ccforms.CCModelChoiceField(
        models.Product.objects.all(),
        label_from_instance=lambda p: "FooLabel {0}".format(unicode(p)),
        choice_attrs=lambda p: {"data-product-id": p.id}
        )
    product2 = ccforms.CCModelChoiceField(models.Product.objects.all())



class CCModelChoiceFieldTest(TestCase):
    """Tests for CCModelChoiceField."""
    def test_label_from_instance(self):
        """Custom label_from_instance callable is used."""
        F.ProductFactory(name="Bar")
        s = unicode(ProductVersionForm()["product"])

        self.assertIn(">FooLabel Bar<", s, s)


    def test_default_label_from_instance(self):
        """Default label_from_instance is unicode of instance."""
        F.ProductFactory(name="Bar")
        s = unicode(ProductVersionForm()["product2"])

        self.assertIn(">Bar<", s, s)


    def test_choice_attrs(self):
        """Custom choice_attrs callable is used."""
        p = F.ProductFactory(name="Bar")
        s = unicode(ProductVersionForm()["product"])

        self.assertIn('data-product-id="{0}"'.format(p.id), s, s)


    def test_set_choices(self):
        """Can set choices explicitly."""
        f = ProductVersionForm()
        f.fields["product"].choices = [(1, "Foo")]
        s = unicode(f["product"])

        self.assertEqual(f.fields["product"].choices, [(1, "Foo")])
        self.assertIn(">Foo<", s, s)
