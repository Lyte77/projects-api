from .models import Testimonial
from rest_framework import serializers

class TestiominialsSerializers(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = ['quote','reviewer_name','reviewer_title','image',
                  'approved','created_at','created_by','updated_at']
        
        read_only_fields = ['created_by', 'created_at', 'updated_at']