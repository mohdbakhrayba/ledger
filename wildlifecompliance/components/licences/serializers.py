from wildlifecompliance.components.licences.models import (
    WildlifeLicence,
    WildlifeLicenceClass,
    WildlifeLicenceActivityType,
    WildlifeLicenceActivity)
from wildlifecompliance.components.applications.serializers import BaseApplicationSerializer
from rest_framework import serializers


class WildlifeLicenceSerializer(serializers.ModelSerializer):
    licence_document = serializers.CharField(
        source='licence_document._file.url')
    status = serializers.CharField(source='get_status_display')
    current_application = BaseApplicationSerializer(read_only=True)

    class Meta:
        model = WildlifeLicence
        fields = (
            'id',
            'licence_document',
            'replaced_by',
            'current_application',
            'activity',
            'region',
            'tenure',
            'title',
            'renewal_sent',
            'issue_date',
            'original_issue_date',
            'start_date',
            'expiry_date',
            'surrender_details',
            'suspension_details',
            'extracted_fields',
            'status'
        )


class DefaultActivitySerializer(serializers.ModelSerializer):
    name = serializers.CharField()

    class Meta:
        model = WildlifeLicenceActivity
        fields = (
            'id',
            'name',
            'base_application_fee',
            'base_licence_fee',
            'short_name'
        )


#    def __init__(self, *args, **kwargs):
#        # Don't pass the 'fields' arg up to the superclass
#        import ipdb; ipdb.set_trace()
#        fields = kwargs.pop('fields', None)
#
#        # Instantiate the superclass normally
#        super(DefaultActivitySerializer, self).__init__(*args, **kwargs)

#    def get_queryset(self):
#        #import ipdb; ipdb.set_trace()
#        user = self.request.user
#		app_ids = Application.objects.filter(Q(org_applicant_id=u.id) | Q(proxy_applicant=u.id) | Q(submitter=u.id)).values_list('id', flat=True).distinct('id')
#		activity_names = ApplicationActivityType.objects.filter(application_id__in=app_ids).values_list('activity_name').distinct()
#		return WildlifeLicenceActivity.objects.filter(name__in=activity_names)


class DefaultActivityTypeSerializer(serializers.ModelSerializer):

    name = serializers.CharField()
    activity = DefaultActivitySerializer(many=True, read_only=True)
    #activity = DefaultActivitySerializer(many=True,read_only=True, queryset=self.qs_purpose())
    class Meta:
        model = WildlifeLicenceActivityType
        fields = (
            'id',
            'name',
            'activity',
            'short_name',
            'not_for_organisation'
        )


#    def qs_purpose(self):
#        #import ipdb; ipdb.set_trace()
#        user = self.request.user
#        app_ids = Application.objects.filter(Q(org_applicant_id=u.id) | Q(proxy_applicant=u.id) | Q(submitter=u.id)).values_list('id', flat=True).distinct('id')
#        activity_names = ApplicationActivityType.objects.filter(application_id__in=app_ids).values_list('activity_name').distinct()
#        return WildlifeLicenceActivity.objects.filter(name__in=activity_names)



class WildlifeLicenceClassSerializer(serializers.ModelSerializer):
    class_status = serializers.SerializerMethodField()
    activity_type = DefaultActivityTypeSerializer(many=True, read_only=True)

    class Meta:
        model = WildlifeLicenceClass
        fields = (
            'id',
            'name',
            'short_name',
            'class_status',
            'activity_type'

        )

    def get_class_status(self, obj):
        return obj.get_licence_class_status_display()


class UserActivitySerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    purpose_in_current_licence = serializers.SerializerMethodField(read_only=True)

    class Meta:
        # list_serializer_class = UserActivityExcludeSerializer
        model = WildlifeLicenceActivity
        fields = (
            'id',
            'name',
            'base_application_fee',
            'base_licence_fee',
            'short_name',
            'purpose_in_current_licence'
        )

    def get_purpose_in_current_licence(self, obj):
        # TODO: 1. need to get a list of all licences for org (if org) or proxy (if proxy) or user
        # TODO: 2. get list of purposes of currently issued licences
        # user_id = self.context['request'].user.id
        # licence_ids = WildlifeLicence.objects.filter()
        # current_purpose_ids =
        # if obj.id in current_purpose_ids:
        #     return True
        return False


class UserActivityTypeSerializer(serializers.ModelSerializer):
    name = serializers.CharField()
    activity = serializers.SerializerMethodField()

    class Meta:
        model = WildlifeLicenceActivityType
        fields = (
            'id',
            'name',
            'activity',
            'short_name',
            'not_for_organisation'
        )

    def get_activity(self, obj):
        activities = self.context.get('activity_records')
        activity_records = activities if activities else obj.activity.all()
        serializer = UserActivitySerializer(
            activity_records,
            many=True,
        )
        return serializer.data


class UserWildlifeLicenceClassSerializer(serializers.ModelSerializer):
    class_status = serializers.SerializerMethodField()
    activity_type = serializers.SerializerMethodField()

    class Meta:
        model = WildlifeLicenceClass
        fields = (
            'id',
            'name',
            'short_name',
            'class_status',
            'activity_type'
        )

    def get_class_status(self, obj):
        return obj.get_licence_class_status_display()

    def get_activity_type(self, obj):
        activities = self.context.get('activity_records')
        activity_type_ids = list(activities.values_list(
            'licence_activity_type_id', flat=True
        )) if activities else []

        activity_types = obj.activity_type.filter(
            id__in=activity_type_ids
        ) if activity_type_ids else obj.activity_type.all()

        serializer = UserActivityTypeSerializer(
            activity_types,
            many=True,
            context={
                'activity_records': activities
            }
        )
        return serializer.data
