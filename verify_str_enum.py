import enum

class OrderStatusEnum(str, enum.Enum):
    PENDING = "pending"

def test_comparison():
    status_from_db = "pending"
    print(f"Comparison 'pending' == OrderStatusEnum.PENDING: {status_from_db == OrderStatusEnum.PENDING}")

if __name__ == "__main__":
    test_comparison()
