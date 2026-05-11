from config import notifications_col

notifications_col.create_index(
    [("studentId", 1), ("assignmentId", 1), ("type", 1)],
    unique=True
)

print("✅ Unique index created")