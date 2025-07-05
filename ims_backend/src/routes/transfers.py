from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from .. import models, schemas, auth
from ..database import get_db
from datetime import datetime
import uuid

router = APIRouter(prefix="/api/transfers", tags=["Transfers"])

# PUBLIC_INTERFACE
@router.get("/", response_model=List[schemas.TransferResponse], summary="Get all transfers")
async def get_transfers(
    skip: int = Query(0, ge=0, description="Number of transfers to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of transfers to return"),
    transfer_type: Optional[str] = Query(None, description="Filter by transfer type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    item_id: Optional[int] = Query(None, description="Filter by item ID"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Get all transfers with optional filtering and pagination
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **transfer_type**: Filter by transfer type (transfer, adjustment, receive, issue)
    - **status**: Filter by status (pending, in_transit, completed, cancelled)
    - **item_id**: Filter by specific item
    
    Requires authentication.
    """
    query = db.query(models.Transfer)
    
    # Apply filters
    if transfer_type:
        query = query.filter(models.Transfer.transfer_type == transfer_type)
    
    if status:
        query = query.filter(models.Transfer.status == status)
    
    if item_id:
        query = query.filter(models.Transfer.item_id == item_id)
    
    transfers = query.order_by(models.Transfer.requested_at.desc()).offset(skip).limit(limit).all()
    
    return [
        schemas.TransferResponse(
            id=transfer.id,
            transfer_number=transfer.transfer_number,
            source_storeroom_id=transfer.source_storeroom_id,
            destination_storeroom_id=transfer.destination_storeroom_id,
            item_id=transfer.item_id,
            quantity=transfer.quantity,
            transfer_type=transfer.transfer_type,
            status=transfer.status,
            reason=transfer.reason,
            notes=transfer.notes,
            source_storeroom={"id": transfer.source_storeroom.id, "name": transfer.source_storeroom.name} if transfer.source_storeroom else None,
            destination_storeroom={"id": transfer.destination_storeroom.id, "name": transfer.destination_storeroom.name} if transfer.destination_storeroom else None,
            item={"id": transfer.item.id, "name": transfer.item.name, "sku": transfer.item.sku} if transfer.item else None,
            requester={"id": transfer.requester.id, "username": transfer.requester.username, "full_name": transfer.requester.full_name} if transfer.requester else None,
            approver={"id": transfer.approver.id, "username": transfer.approver.username, "full_name": transfer.approver.full_name} if transfer.approver else None,
            completer={"id": transfer.completer.id, "username": transfer.completer.username, "full_name": transfer.completer.full_name} if transfer.completer else None,
            requested_at=transfer.requested_at,
            approved_at=transfer.approved_at,
            completed_at=transfer.completed_at
        ) for transfer in transfers
    ]

# PUBLIC_INTERFACE
@router.get("/{transfer_id}", response_model=schemas.TransferResponse, summary="Get transfer by ID")
async def get_transfer(
    transfer_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Get a specific transfer by ID
    
    - **transfer_id**: Transfer ID to retrieve
    
    Requires authentication.
    """
    transfer = db.query(models.Transfer).filter(models.Transfer.id == transfer_id).first()
    if not transfer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transfer not found")
    
    return schemas.TransferResponse(
        id=transfer.id,
        transfer_number=transfer.transfer_number,
        source_storeroom_id=transfer.source_storeroom_id,
        destination_storeroom_id=transfer.destination_storeroom_id,
        item_id=transfer.item_id,
        quantity=transfer.quantity,
        transfer_type=transfer.transfer_type,
        status=transfer.status,
        reason=transfer.reason,
        notes=transfer.notes,
        source_storeroom={"id": transfer.source_storeroom.id, "name": transfer.source_storeroom.name} if transfer.source_storeroom else None,
        destination_storeroom={"id": transfer.destination_storeroom.id, "name": transfer.destination_storeroom.name} if transfer.destination_storeroom else None,
        item={"id": transfer.item.id, "name": transfer.item.name, "sku": transfer.item.sku} if transfer.item else None,
        requester={"id": transfer.requester.id, "username": transfer.requester.username, "full_name": transfer.requester.full_name} if transfer.requester else None,
        approver={"id": transfer.approver.id, "username": transfer.approver.username, "full_name": transfer.approver.full_name} if transfer.approver else None,
        completer={"id": transfer.completer.id, "username": transfer.completer.username, "full_name": transfer.completer.full_name} if transfer.completer else None,
        requested_at=transfer.requested_at,
        approved_at=transfer.approved_at,
        completed_at=transfer.completed_at
    )

# PUBLIC_INTERFACE
@router.post("/", response_model=schemas.TransferResponse, summary="Create new transfer")
async def create_transfer(
    transfer: schemas.TransferCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Create a new transfer
    
    - **source_storeroom_id**: Source storeroom ID (optional for receive/adjustment)
    - **destination_storeroom_id**: Destination storeroom ID (optional for issue/adjustment)
    - **item_id**: Item ID to transfer
    - **quantity**: Quantity to transfer
    - **transfer_type**: Type of transfer (transfer, adjustment, receive, issue)
    - **reason**: Reason for transfer
    - **notes**: Additional notes
    
    Requires authentication. Users can create transfers.
    """
    # Validate item exists
    item = db.query(models.Item).filter(models.Item.id == transfer.item_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Item not found")
    
    # Validate storerooms exist
    if transfer.source_storeroom_id:
        source_storeroom = db.query(models.Storeroom).filter(models.Storeroom.id == transfer.source_storeroom_id).first()
        if not source_storeroom:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Source storeroom not found")
    
    if transfer.destination_storeroom_id:
        destination_storeroom = db.query(models.Storeroom).filter(models.Storeroom.id == transfer.destination_storeroom_id).first()
        if not destination_storeroom:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Destination storeroom not found")
    
    # Validate transfer type requirements
    if transfer.transfer_type == "transfer":
        if not transfer.source_storeroom_id or not transfer.destination_storeroom_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Transfer requires both source and destination storerooms")
    elif transfer.transfer_type == "receive":
        if not transfer.destination_storeroom_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Receive requires destination storeroom")
    elif transfer.transfer_type == "issue":
        if not transfer.source_storeroom_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Issue requires source storeroom")
    
    # Check available quantity for source storeroom
    if transfer.source_storeroom_id:
        storeroom_item = db.query(models.StoreroomItem).filter(
            models.StoreroomItem.storeroom_id == transfer.source_storeroom_id,
            models.StoreroomItem.item_id == transfer.item_id
        ).first()
        if not storeroom_item or storeroom_item.available_quantity < transfer.quantity:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Insufficient available quantity in source storeroom")
    
    # Generate transfer number
    transfer_number = f"TRN-{datetime.utcnow().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
    
    # Create transfer
    db_transfer = models.Transfer(
        transfer_number=transfer_number,
        source_storeroom_id=transfer.source_storeroom_id,
        destination_storeroom_id=transfer.destination_storeroom_id,
        item_id=transfer.item_id,
        quantity=transfer.quantity,
        transfer_type=transfer.transfer_type,
        reason=transfer.reason,
        notes=transfer.notes,
        requested_by=current_user.id,
        status="pending"
    )
    
    db.add(db_transfer)
    db.commit()
    db.refresh(db_transfer)
    
    # Create transfer log
    transfer_log = models.TransferLog(
        transfer_id=db_transfer.id,
        action="created",
        new_status="pending",
        user_id=current_user.id,
        notes=f"Transfer created by {current_user.username}"
    )
    
    db.add(transfer_log)
    db.commit()
    
    return schemas.TransferResponse(
        id=db_transfer.id,
        transfer_number=db_transfer.transfer_number,
        source_storeroom_id=db_transfer.source_storeroom_id,
        destination_storeroom_id=db_transfer.destination_storeroom_id,
        item_id=db_transfer.item_id,
        quantity=db_transfer.quantity,
        transfer_type=db_transfer.transfer_type,
        status=db_transfer.status,
        reason=db_transfer.reason,
        notes=db_transfer.notes,
        source_storeroom={"id": db_transfer.source_storeroom.id, "name": db_transfer.source_storeroom.name} if db_transfer.source_storeroom else None,
        destination_storeroom={"id": db_transfer.destination_storeroom.id, "name": db_transfer.destination_storeroom.name} if db_transfer.destination_storeroom else None,
        item={"id": db_transfer.item.id, "name": db_transfer.item.name, "sku": db_transfer.item.sku} if db_transfer.item else None,
        requester={"id": db_transfer.requester.id, "username": db_transfer.requester.username, "full_name": db_transfer.requester.full_name} if db_transfer.requester else None,
        approver=None,
        completer=None,
        requested_at=db_transfer.requested_at,
        approved_at=db_transfer.approved_at,
        completed_at=db_transfer.completed_at
    )

# PUBLIC_INTERFACE
@router.put("/{transfer_id}/approve", response_model=schemas.TransferResponse, summary="Approve transfer")
async def approve_transfer(
    transfer_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Approve a transfer
    
    - **transfer_id**: Transfer ID to approve
    
    Requires admin or manager privileges.
    """
    # Check permissions
    if current_user.role.name not in ["admin", "manager"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    
    transfer = db.query(models.Transfer).filter(models.Transfer.id == transfer_id).first()
    if not transfer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transfer not found")
    
    if transfer.status != "pending":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Transfer is not pending")
    
    # Update transfer
    transfer.status = "approved"
    transfer.approved_by = current_user.id
    transfer.approved_at = datetime.utcnow()
    
    # Create transfer log
    transfer_log = models.TransferLog(
        transfer_id=transfer.id,
        action="approved",
        previous_status="pending",
        new_status="approved",
        user_id=current_user.id,
        notes=f"Transfer approved by {current_user.username}"
    )
    
    db.add(transfer_log)
    db.commit()
    db.refresh(transfer)
    
    return schemas.TransferResponse(
        id=transfer.id,
        transfer_number=transfer.transfer_number,
        source_storeroom_id=transfer.source_storeroom_id,
        destination_storeroom_id=transfer.destination_storeroom_id,
        item_id=transfer.item_id,
        quantity=transfer.quantity,
        transfer_type=transfer.transfer_type,
        status=transfer.status,
        reason=transfer.reason,
        notes=transfer.notes,
        source_storeroom={"id": transfer.source_storeroom.id, "name": transfer.source_storeroom.name} if transfer.source_storeroom else None,
        destination_storeroom={"id": transfer.destination_storeroom.id, "name": transfer.destination_storeroom.name} if transfer.destination_storeroom else None,
        item={"id": transfer.item.id, "name": transfer.item.name, "sku": transfer.item.sku} if transfer.item else None,
        requester={"id": transfer.requester.id, "username": transfer.requester.username, "full_name": transfer.requester.full_name} if transfer.requester else None,
        approver={"id": transfer.approver.id, "username": transfer.approver.username, "full_name": transfer.approver.full_name} if transfer.approver else None,
        completer={"id": transfer.completer.id, "username": transfer.completer.username, "full_name": transfer.completer.full_name} if transfer.completer else None,
        requested_at=transfer.requested_at,
        approved_at=transfer.approved_at,
        completed_at=transfer.completed_at
    )

# PUBLIC_INTERFACE
@router.put("/{transfer_id}/complete", response_model=schemas.TransferResponse, summary="Complete transfer")
async def complete_transfer(
    transfer_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Complete a transfer and update inventory
    
    - **transfer_id**: Transfer ID to complete
    
    Requires admin or manager privileges.
    """
    # Check permissions
    if current_user.role.name not in ["admin", "manager"]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    
    transfer = db.query(models.Transfer).filter(models.Transfer.id == transfer_id).first()
    if not transfer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transfer not found")
    
    if transfer.status not in ["approved", "in_transit"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Transfer must be approved or in transit")
    
    # Update inventory
    if transfer.source_storeroom_id:
        # Reduce quantity from source
        source_item = db.query(models.StoreroomItem).filter(
            models.StoreroomItem.storeroom_id == transfer.source_storeroom_id,
            models.StoreroomItem.item_id == transfer.item_id
        ).first()
        if source_item:
            source_item.quantity -= transfer.quantity
            if source_item.quantity < 0:
                source_item.quantity = 0
    
    if transfer.destination_storeroom_id:
        # Add quantity to destination
        dest_item = db.query(models.StoreroomItem).filter(
            models.StoreroomItem.storeroom_id == transfer.destination_storeroom_id,
            models.StoreroomItem.item_id == transfer.item_id
        ).first()
        if dest_item:
            dest_item.quantity += transfer.quantity
        else:
            # Create new storeroom item
            dest_item = models.StoreroomItem(
                storeroom_id=transfer.destination_storeroom_id,
                item_id=transfer.item_id,
                quantity=transfer.quantity
            )
            db.add(dest_item)
    
    # Update transfer
    transfer.status = "completed"
    transfer.completed_by = current_user.id
    transfer.completed_at = datetime.utcnow()
    
    # Create transfer log
    transfer_log = models.TransferLog(
        transfer_id=transfer.id,
        action="completed",
        previous_status=transfer.status,
        new_status="completed",
        user_id=current_user.id,
        notes=f"Transfer completed by {current_user.username}"
    )
    
    db.add(transfer_log)
    db.commit()
    db.refresh(transfer)
    
    return schemas.TransferResponse(
        id=transfer.id,
        transfer_number=transfer.transfer_number,
        source_storeroom_id=transfer.source_storeroom_id,
        destination_storeroom_id=transfer.destination_storeroom_id,
        item_id=transfer.item_id,
        quantity=transfer.quantity,
        transfer_type=transfer.transfer_type,
        status=transfer.status,
        reason=transfer.reason,
        notes=transfer.notes,
        source_storeroom={"id": transfer.source_storeroom.id, "name": transfer.source_storeroom.name} if transfer.source_storeroom else None,
        destination_storeroom={"id": transfer.destination_storeroom.id, "name": transfer.destination_storeroom.name} if transfer.destination_storeroom else None,
        item={"id": transfer.item.id, "name": transfer.item.name, "sku": transfer.item.sku} if transfer.item else None,
        requester={"id": transfer.requester.id, "username": transfer.requester.username, "full_name": transfer.requester.full_name} if transfer.requester else None,
        approver={"id": transfer.approver.id, "username": transfer.approver.username, "full_name": transfer.approver.full_name} if transfer.approver else None,
        completer={"id": transfer.completer.id, "username": transfer.completer.username, "full_name": transfer.completer.full_name} if transfer.completer else None,
        requested_at=transfer.requested_at,
        approved_at=transfer.approved_at,
        completed_at=transfer.completed_at
    )

# PUBLIC_INTERFACE
@router.get("/{transfer_id}/logs", response_model=List[schemas.TransferLogResponse], summary="Get transfer logs")
async def get_transfer_logs(
    transfer_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Get logs for a specific transfer
    
    - **transfer_id**: Transfer ID
    
    Requires authentication.
    """
    transfer = db.query(models.Transfer).filter(models.Transfer.id == transfer_id).first()
    if not transfer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transfer not found")
    
    logs = db.query(models.TransferLog).filter(models.TransferLog.transfer_id == transfer_id).order_by(models.TransferLog.timestamp.desc()).all()
    
    return [
        schemas.TransferLogResponse(
            id=log.id,
            transfer_id=log.transfer_id,
            action=log.action,
            previous_status=log.previous_status,
            new_status=log.new_status,
            user={"id": log.user.id, "username": log.user.username, "full_name": log.user.full_name} if log.user else None,
            timestamp=log.timestamp,
            notes=log.notes
        ) for log in logs
    ]
