from unittest import mock

import pytest
from django.test import TestCase
from rest_framework import serializers
from rest_framework.serializers import ListSerializer, Serializer

from ambient_toolbox.drf.fields import RecursiveField
from testapp.models import ModelWithFkToSelf, ModelWithOneToOneToSelf


class TestManyTrueSerializer(serializers.ModelSerializer):
    children = RecursiveField(many=True)

    class Meta:
        model = ModelWithFkToSelf
        fields = [
            "id",
            "children",
        ]


@pytest.mark.skip
class TestManyFalseSerializer(serializers.ModelSerializer):
    peer = RecursiveField()

    class Meta:
        model = ModelWithOneToOneToSelf
        fields = [
            "id",
            "peer",
        ]


class RecursiveFieldTest(TestCase):
    @mock.patch.object(Serializer, "update")
    def test_update_super_called(self, mocked_update):
        field = RecursiveField()
        field.update(instance=None, validated_data={})

        mocked_update.assert_called_once_with(None, {})

    @mock.patch.object(Serializer, "create")
    def test_create_super_called(self, mocked_create):
        field = RecursiveField()
        field.create(validated_data={})

        mocked_create.assert_called_once_with({})

    def test_many_true_regular(self):
        serializer = TestManyTrueSerializer()

        self.assertIn("children", serializer.fields)
        self.assertIsInstance(serializer.fields["children"], ListSerializer)
        self.assertIsInstance(serializer.fields["children"].child, RecursiveField)

    def test_many_true_representation(self):
        mwfts_1 = ModelWithFkToSelf.objects.create(parent=None)
        mwfts_2 = ModelWithFkToSelf.objects.create(parent=mwfts_1)

        serializer = TestManyTrueSerializer(instance=mwfts_1)
        representation = serializer.to_representation(instance=mwfts_1)

        self.assertIsInstance(representation, dict)
        self.assertIn("children", representation)
        self.assertEqual(len(representation["children"]), 1)
        self.assertEqual(representation["children"][0]["id"], mwfts_2.id)
        self.assertEqual(representation["children"][0]["children"], [])

    def test_many_false_regular(self):
        serializer = TestManyFalseSerializer()

        self.assertIn("peer", serializer.fields)
        self.assertIsInstance(serializer.fields["peer"], RecursiveField)

    def test_many_false_representation(self):
        mwotos_no_peer = ModelWithOneToOneToSelf.objects.create(peer=None)
        mwotos_has_peer = ModelWithOneToOneToSelf.objects.create(peer=mwotos_no_peer)

        serializer = TestManyFalseSerializer(instance=mwotos_has_peer)
        representation = serializer.to_representation(instance=mwotos_has_peer)

        self.assertIsInstance(representation, dict)
        self.assertIn("peer", representation)
        self.assertEqual(len(representation["peer"]), 2)
        self.assertEqual(representation["peer"]["id"], mwotos_no_peer.id)
        self.assertEqual(representation["peer"]["peer"], None)
