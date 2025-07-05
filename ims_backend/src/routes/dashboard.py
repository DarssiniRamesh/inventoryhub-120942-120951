from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from .. import models, auth
from ..database import get_db

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])

# PUBLIC_INTERFACE
@router.get("/stats", summary="Get dashboard statistics")
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Get dashboard statistics overview
    
    Returns counts and summaries for dashboard display.
    Requires authentication.
    """
    # Get total counts
    total_items = db.query(models.Item).filter(models.Item.is_active == True).count()
    total_storerooms = db.query(models.Storeroom).filter(models.Storeroom.is_active == True).count()
    total_users = db.query(models.User).filter(models.User.is_active == True).count()
    
    # Get transfer statistics
    pending_transfers = db.query(models.Transfer).filter(models.Transfer.status == "pending").count()
    completed_transfers = db.query(models.Transfer).filter(models.Transfer.status == "completed").count()
    
    # Get low stock items
    low_stock_items = db.query(models.Item).join(models.StoreroomItem).filter(
        and_(
            models.Item.is_active == True,
            models.StoreroomItem.quantity <= models.Item.minimum_stock,
            models.Item.minimum_stock > 0
        )
    ).distinct().count()
    
    # Get total inventory value (approximation)
    total_inventory_value = db.query(
        func.sum(models.StoreroomItem.quantity * models.Item.unit_cost)
    ).join(models.Item).filter(
        and_(
            models.Item.unit_cost.isnot(None),
            models.Item.is_active == True
        )
    ).scalar() or 0
    
    # Get recent transfers
    recent_transfers = db.query(models.Transfer).order_by(
        models.Transfer.requested_at.desc()
    ).limit(5).all()
    
    # Get storeroom summaries
    storeroom_summaries = db.query(
        models.Storeroom.id,
        models.Storeroom.name,
        func.count(models.StoreroomItem.id).label('item_count'),
        func.sum(models.StoreroomItem.quantity).label('total_quantity')
    ).join(
        models.StoreroomItem, models.Storeroom.id == models.StoreroomItem.storeroom_id, isouter=True
    ).filter(
        models.Storeroom.is_active == True
    ).group_by(
        models.Storeroom.id, models.Storeroom.name
    ).all()
    
    return {
        "overview": {
            "total_items": total_items,
            "total_storerooms": total_storerooms,
            "total_users": total_users,
            "pending_transfers": pending_transfers,
            "completed_transfers": completed_transfers,
            "low_stock_items": low_stock_items,
            "total_inventory_value": float(total_inventory_value)
        },
        "recent_transfers": [
            {
                "id": t.id,
                "transfer_number": t.transfer_number,
                "item_name": t.item.name if t.item else None,
                "source_storeroom": t.source_storeroom.name if t.source_storeroom else None,
                "destination_storeroom": t.destination_storeroom.name if t.destination_storeroom else None,
                "quantity": t.quantity,
                "status": t.status,
                "requested_at": t.requested_at
            } for t in recent_transfers
        ],
        "storeroom_summaries": [
            {
                "id": s.id,
                "name": s.name,
                "item_count": s.item_count or 0,
                "total_quantity": s.total_quantity or 0
            } for s in storeroom_summaries
        ]
    }

# PUBLIC_INTERFACE
@router.get("/low-stock", summary="Get low stock items")
async def get_low_stock_items(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Get items with low stock levels
    
    Returns items where current quantity is at or below minimum stock level.
    Requires authentication.
    """
    low_stock_query = db.query(
        models.Item,
        models.StoreroomItem.quantity,
        models.StoreroomItem.storeroom_id,
        models.Storeroom.name.label('storeroom_name')
    ).join(
        models.StoreroomItem
    ).join(
        models.Storeroom
    ).filter(
        and_(
            models.Item.is_active == True,
            models.StoreroomItem.quantity <= models.Item.minimum_stock,
            models.Item.minimum_stock > 0
        )
    ).all()
    
    return [
        {
            "item_id": item.Item.id,
            "item_name": item.Item.name,
            "sku": item.Item.sku,
            "category": item.Item.category,
            "current_quantity": item.quantity,
            "minimum_stock": item.Item.minimum_stock,
            "storeroom_id": item.storeroom_id,
            "storeroom_name": item.storeroom_name,
            "unit_of_measure": item.Item.unit_of_measure
        } for item in low_stock_query
    ]
