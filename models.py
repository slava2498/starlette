from tortoise import fields, models

class Users(models.Model):
    id = fields.IntField(pk=True)
    email = fields.CharField(max_length=50)

    def __str__(self) -> str:
        return f"User {self.id}: {self.username}"