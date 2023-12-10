# Generated by Django 4.2.5 on 2023-12-10 12:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("reviews_app", "0003_alter_reviews_orderid"),
    ]

    operations = [
        migrations.CreateModel(
            name="CEOReviews",
            fields=[
                ("ceoReviewId", models.BigAutoField(primary_key=True, serialize=False)),
                ("content", models.CharField(blank=True, max_length=255, null=True)),
                ("createdDate", models.DateTimeField(auto_now_add=True)),
                ("modifiedDate", models.DateTimeField(auto_now=True)),
                ("status", models.CharField(default="일반", max_length=255)),
                (
                    "reviewId",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="review",
                        to="reviews_app.reviews",
                    ),
                ),
            ],
        ),
    ]
