import datetime
from sqlalchemy.future import select
from app.db.database import init_db, AsyncSessionLocal
from app.domain.models import Tenant, User, Order, Forecast, Recommendation

async def test_models_relationships():
    # Initialize DB
    await init_db()
    
    async with AsyncSessionLocal() as session:
        # Create Dummy Tenant
        tenant = Tenant(name="Test Tenant")
        session.add(tenant)
        await session.commit()
        await session.refresh(tenant)
        
        # Create Dummy User
        user = User(tenant_id=tenant.id, email="test_user_models@test.com", hashed_password="pw")
        session.add(user)
        
        # Create Dummy Order
        order = Order(tenant_id=tenant.id, due_date=datetime.datetime.utcnow())
        session.add(order)
        
        # Create Dummy Forecast
        forecast = Forecast(tenant_id=tenant.id, sku_id="SKU1", location_id="LOC1", predicted_demand=100.0)
        session.add(forecast)
        await session.commit()
        await session.refresh(forecast)
        
        # Create Dummy Recommendation
        rec = Recommendation(tenant_id=tenant.id, forecast_id=forecast.id, action_type="order_more")
        session.add(rec)
        await session.commit()
        
        # Retrieve and Verify
        result = await session.execute(select(Tenant).where(Tenant.id == tenant.id))
        fetched_tenant = result.scalars().first()
        assert fetched_tenant is not None
        assert fetched_tenant.name == "Test Tenant"
        
        # Verify related user
        user_res = await session.execute(select(User).where(User.tenant_id == fetched_tenant.id))
        fetched_user = user_res.scalars().first()
        assert fetched_user is not None
        assert fetched_user.email == "test_user_models@test.com"
        
        # Verify order
        order_res = await session.execute(select(Order).where(Order.tenant_id == fetched_tenant.id))
        fetched_order = order_res.scalars().first()
        assert fetched_order is not None
        
        # Verify forecast & recommendation
        rec_res = await session.execute(select(Recommendation).where(Recommendation.tenant_id == fetched_tenant.id))
        fetched_rec = rec_res.scalars().first()
        assert fetched_rec is not None
        assert fetched_rec.forecast_id == forecast.id
