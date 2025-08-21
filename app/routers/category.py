from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Category
from app.schemas import CategoryCreate, CategoryRead, PagedResponse, OurBaseModelOut, CategoryUpdate, UserRead, BaseFilter
from app.routers.error import get_error_detail,add_error
import cloudinary.uploader
from app.utils import convert_to_createCategorySchema, convert_to_updateCategorySchema
from app.oauth2 import get_current_user

router = APIRouter(prefix="/categories", tags=["Categories"])

error_keys={
     "categories_pkey":{"message":"Category not found","status":404},
     "categories_user_id_fkey":{"message":"User not found","status":404}
}

@router.post("/")
def create_category(category: CategoryCreate = Depends(convert_to_createCategorySchema), db: Session = Depends(get_db), user_id: int = 1, category_image: UploadFile = File(...), current_user: UserRead = Depends(get_current_user)):
    try:
        new_category = category.model_dump()
        image_data = cloudinary.uploader.upload(category_image.file)
        new_category["image_link"] = image_data.get("secure_url")
        new_category["public_id"] = image_data.get("public_id")
        db_category = Category(**new_category, user_id=user_id)
        db.add(db_category)
        db.commit()
        return OurBaseModelOut (status=201, message="Category created successfully")
    except Exception as e:
        db.rollback()
        add_error(str(e),db,current_user.id)

        if(new_category.get("public_id")):
            cloudinary.uploader.destroy(new_category.get("public_id"))
            
        error_detail = get_error_detail(str(e), error_keys)
        return OurBaseModelOut(status=error_detail["status"], message=error_detail["message"])

@router.get("/")
def get_categories(db: Session = Depends(get_db),filter: BaseFilter = Depends() , current_user: UserRead = Depends(get_current_user)):
    try:
        query = db.query(Category)

        if filter.name_substr:
            query = query.filter(Category.name.ilike(f"%{filter.name_substr}%"))
        
        total_records = query.count()
        categories = query.offset((filter.page_number - 1) * filter.page_size).limit(filter.page_size).all()
        total_pages = (total_records + filter.page_size - 1) // filter.page_size
        return PagedResponse[CategoryRead](
            data=[CategoryRead.model_validate(c) for c in categories],
            page_number=filter.page_number,
            page_size=filter.page_size,
            total_pages=total_pages,
            total_records=total_records,
            status=200,
            message="Categories fetched"
        )
    except Exception as e:
        error_detail=get_error_detail(str(e), error_keys)
        return OurBaseModelOut(status=error_detail["status"], message=error_detail["message"]) 

@router.get("/{category_id}")
def get_category(category_id: int, db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_user)):
    try:
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            return OurBaseModelOut(status=404, message="Category not found")
        return CategoryRead.model_validate(category)
    except Exception as e:
        error_detail = get_error_detail(str(e),error_keys)
        return OurBaseModelOut(status=error_detail["status"], message=error_detail["message"]) 

@router.put("/{category_id}")
def update_category(category_id: int, category: CategoryUpdate = Depends(convert_to_updateCategorySchema), db: Session = Depends(get_db), category_image: UploadFile = File(None), current_user: UserRead = Depends(get_current_user)):
    try:
        new_data = {}
        uploaded_public_id = None
        db_category = db.query(Category).filter(Category.id == category_id).first()

        if not db_category:
            return OurBaseModelOut(status=404, message="Category not found")
        
        new_data = category.model_dump(exclude_unset=True)

        if category_image:
            image_data = cloudinary.uploader.upload(category_image.file)
            uploaded_public_id = image_data.get("public_id")
            new_data["public_id"] = uploaded_public_id
            new_data["image_link"] = image_data.get("secure_url")
        
        for key, value in new_data.items():
            setattr(db_category, key, value)

        db.commit()
        db.refresh(db_category)

        if category_image and db_category.public_id != uploaded_public_id:
            cloudinary.uploader.destroy(db_category.public_id)

        return OurBaseModelOut(status=200, message="Category updated successfully")
    except Exception as e:
        db.rollback()
        add_error(str(e),db,current_user.id)

        if(uploaded_public_id):
            cloudinary.uploader.destroy(uploaded_public_id)
        
        error_detail = get_error_detail(str(e),error_keys)
        return OurBaseModelOut(status=error_detail["status"], message=error_detail["message"]) 


@router.delete("/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_user)):
    try:
        query = db.query(Category).filter(Category.id == category_id)
        db_category = query.first()

        if not db_category:
            return OurBaseModelOut(status=404, message="Category not found")
        
        cloudinary.uploader.destroy(db_category.public_id)
        query.delete()
        db.commit()
        return OurBaseModelOut(status=200, message="Category deleted successfully")
    except Exception as e:
        db.rollback()
        add_error(str(e),db,current_user.id)
        error_detail = get_error_detail(str(e),error_keys)
        return OurBaseModelOut(status=error_detail["status"], message=error_detail["message"]) 
