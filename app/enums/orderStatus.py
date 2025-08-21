from enum import Enum

class OrderStatus(Enum):
    Pending = "Pending"
    Paid = "Paid"
    Shipped = "Shipped"
    Completed = "Completed"
    Cancelled = "Cancelled"