from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session as DbSession
from app.database import get_db
from app.schemas import OrderBase, OrderRead, OurBaseModelOut, PagedResponse, UserRead, BaseFilter
from app.models import Order, OrderItem, Session
from app.routers.error import add_error, get_error_detail
from app.oauth2 import get_current_user
from app.routers.session import get_active_session

router = APIRouter(prefix="/orders", tags=["Orders"])

error_keys={
    "orders_pkey": {"message": "Order not found", "status": 404},
    "order_items_pkey": {"message": "Order item not found", "status": 404},
    "order_items_order_id_fkey": {"message": "Order not found", "status": 404},
    "order_items_product_id_fkey": {"message": "Product not found", "status": 404},
    "orders_buyer_id_fkey":{"message":"Buyer with this id not found","status":404},
    "orders_session_id_fkey":{"message":"Session not found","status":404}
}

@router.post("/")
def create_order(order: OrderBase, db: DbSession = Depends(get_db), current_user: UserRead = Depends(get_current_user)):
    try:
        active_session = get_active_session(db,current_user.id)
        new_order = Order(
            buyer_id=order.buyer_id,
            buyer_phone=order.buyer_phone,
            buyer_address=order.buyer_address,
            session_id=active_session.id
        )
    
        db.add(new_order)
        db.flush()
        db.bulk_save_objects([OrderItem(order_id = new_order.id, product_id = item.product_id, quantity = item.quantity, unit_price = item.unit_price) for item in order.items])
        db.commit()
        return OurBaseModelOut(status=201, message="Order created successfully")

    except Exception as e:
        db.rollback()
        add_error(str(e),db,current_user.id)
        error_detail = get_error_detail(str(e),error_keys)
        return OurBaseModelOut(status=error_detail["status"], message=error_detail["message"])



@router.get("/{order_id}")
def get_order(order_id: int, db: DbSession = Depends(get_db), current_user: UserRead = Depends(get_current_user)):
   try:
        order = db.query(Order).filter(Order.id == order_id).first()
        if not order:
            return OurBaseModelOut(status=404, message="Order not found")
        return OrderRead.model_validate(order)
   
   except Exception as e:
       error_detail = get_error_detail(str(e),error_keys)
       return OurBaseModelOut(status=error_detail["status"], message=error_detail["message"])


@router.get("/")
def get_orders(db: DbSession = Depends(get_db),filter: BaseFilter = Depends(), current_user: UserRead = Depends(get_current_user)):
    try:
        query = db.query(Order)
        total_records = query.count()
        orders = query.offset((filter.page_number - 1) * filter.page_size).limit(filter.page_size).all()
        total_pages = (total_records + filter.page_size - 1) // filter.page_size
        return PagedResponse[OrderRead](
            data=[OrderRead.model_validate(o) for o in orders],
            page_number=filter.page_number,
            page_size=filter.page_size,
            total_pages=total_pages,
            total_records=total_records,
            status=200,
            message="Orders fetched"
        )
        
    except Exception as e:
        error_detail=get_error_detail(str(e), error_keys)
        return OurBaseModelOut(status=error_detail["status"], message=error_detail["message"])


@router.put("/{order_id}")
def update_order_status(order_id: int, status: str, db: DbSession = Depends(get_db), current_user: UserRead = Depends(get_current_user)):
    try:
        updated_rows = db.query(Order).filter(Order.id == order_id).update({"status": status})
        if not updated_rows:
            return OurBaseModelOut(status=404, message="Order not found")
    
        db.commit()
        return OurBaseModelOut(status=200, message="Order updated successfully")

    except Exception as e:
        db.rollback()
        add_error(str(e),db,current_user.id)
        error_detail=get_error_detail(str(e), error_keys)
        return OurBaseModelOut(status=error_detail["status"], message=error_detail["message"])


@router.delete("/{order_id}")
def delete_order(order_id: int, db: DbSession = Depends(get_db), current_user: UserRead = Depends(get_current_user)):
    try:
        order = db.query(Order).filter(Order.id == order_id).delete()
        if not order:
            return OurBaseModelOut(status=404, message="Order not found")
        db.commit()
        return OurBaseModelOut(status=200, message="Order deleted successfully")

    except Exception as e:
        db.rollback()
        add_error(str(e),db,current_user.id)
        error_detail=get_error_detail(str(e), error_keys)
        return OurBaseModelOut(status=error_detail["status"], message=error_detail["message"])