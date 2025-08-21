from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models import Product
from app.database import get_db
from app.schemas import ProductCreate, ProductOut, ProductUpdate, OurBaseModelOut, PagedResponse, UserRead, BaseFilter
from app.routers.error import get_error_detail,add_error
from app.oauth2 import get_current_user


router = APIRouter(prefix="/products", tags=["Products"])

error_keys={
    "products_pkey":{"message":"Product not found","status":404},
    "products_category_id_fkey":{"message":"Category not found","status":404}
}

@router.post("/")
def create_product(product: ProductCreate,db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_user)):
   try:
        new_product = Product(**product.model_dump())
        db.add(new_product)
        db.commit()
        return OurBaseModelOut(status=201,message="Product created successfully") 
   except Exception as e:
        db.rollback()
        add_error(str(e),db,current_user.id)
        error_detail = get_error_detail(str(e),error_keys)
        return OurBaseModelOut(status=error_detail["status"], message=error_detail["message"])
   

@router.get("/")
def get_products(db: Session = Depends(get_db),filter: BaseFilter = Depends(), current_user: UserRead = Depends(get_current_user)):
    try:
        query = db.query(Product)
        
        if filter.name_substr:
            query = query.filter(Product.name.ilike(f"%{filter.name_substr}%"))

        total_records = query.count()
        products= query.offset((filter.page_number - 1) * filter.page_size).limit(filter.page_size).all()
        total_pages = (total_records + filter.page_size - 1) // filter.page_size
        return PagedResponse[ProductOut](
            data=[ProductOut.model_validate(p) for p in products],
            page_number=filter.page_number,
            page_size=filter.page_size,
            total_pages=total_pages,
            total_records=total_records,
            status=200,
            message="Products fetched"
        )
    except Exception as e:
        error_detail=get_error_detail(str(e), error_keys)
        return OurBaseModelOut(status=error_detail["status"], message=error_detail["message"])

@router.get("/{product_id}")
def get_product(product_id: int, db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_user)):
    try:
        product = db.query(Product).filter(Product.id == product_id).first()

        if not product:
            return OurBaseModelOut(status=404, message="Product not found")
        
        return ProductOut.model_validate(product)      
    except Exception as e:      
        error_detail=get_error_detail(str(e), error_keys)
        return OurBaseModelOut(status=error_detail["status"], message=error_detail["message"])

@router.put("/{product_id}")
def update_product(product_id: int,product_update: ProductUpdate,db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_user)):
   try:
        product = db.query(Product).filter(Product.id == product_id).first()
        
        if not product:
           return OurBaseModelOut(status=404, message="Product not found")

        for key, value in product_update.model_dump(exclude_unset=True).items():
            setattr(product, key, value)

        db.commit()
        return OurBaseModelOut(status=200, message="Product updated successfully")
   except Exception as e:
        db.rollback()
        add_error(str(e),db,current_user.id)
        error_detail = get_error_detail(str(e), error_keys)
        return OurBaseModelOut(status=error_detail["status"], message=error_detail["message"])

@router.delete("/{product_id}")
def delete_product(product_id: int,db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_user)):
    try:
        query = db.query(Product).filter(Product.id == product_id)
        product = query.first()

        if not product:
            return OurBaseModelOut(status=404, message="Product not found")

        query.delete()
        db.commit()
        return OurBaseModelOut(status=200, message="Product deleted successfully")
    except Exception as e:
        db.rollback()
        add_error(str(e),db,current_user.id)
        error_detail = get_error_detail(str(e), error_keys)
        return OurBaseModelOut(status=error_detail["status"], message=error_detail["message"])
