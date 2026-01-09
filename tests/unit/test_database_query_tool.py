import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from execution.models.database import Base, DataAdministration
from execution.tools.database_query_tool import DatabaseQueryTool

@pytest.fixture
async def sqlite_db():
    """Setup an in-memory SQLite database for testing."""
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    # Seed some data
    async with async_session_maker() as session:
        session.add(DataAdministration(
            id_data_administration='facturation_client_1',
            nom_client='ALTECA',
            annee=2025,
            prix_unitaire='500',
            tva='20 %'
        ))
        session.add(DataAdministration(
            id_data_administration='charge_locative_1',
            annee=2025,
            charges={"items": [{"desc": "test", "amount": 10}]}
        ))
        await session.commit()
        
    yield async_session_maker
    await engine.dispose()

@pytest.mark.asyncio
async def test_facture_info_query(sqlite_db):
    tool = DatabaseQueryTool()
    
    # Mock DatabaseManager to use our sqlite_db
    with patch('execution.tools.database_query_tool.DatabaseManager') as mock_db_mgr:
        instance = mock_db_mgr.return_value
        instance.async_session_maker = sqlite_db
        instance.close = AsyncMock()
        
        result = await tool._arun(
            query_type="facture_info",
            filters={"client": "ALTECA", "annee": 2025}
        )
        
        assert result["nom_client"] == "ALTECA"
        assert result["annee"] == 2025
        assert result["id_data_administration"] == "facturation_client_1"

@pytest.mark.asyncio
async def test_charges_info_query(sqlite_db):
    tool = DatabaseQueryTool()
    
    with patch('execution.tools.database_query_tool.DatabaseManager') as mock_db_mgr:
        instance = mock_db_mgr.return_value
        instance.async_session_maker = sqlite_db
        instance.close = AsyncMock()
        
        result = await tool._arun(
            query_type="charges_info",
            filters={"annee": 2025}
        )
        
        assert result["annee"] == 2025
        assert result["id_data_administration"] == "charge_locative_1"
        assert result["charges"] == {"items": [{"desc": "test", "amount": 10}]}

@pytest.mark.asyncio
async def test_query_invalid_type(sqlite_db):
    tool = DatabaseQueryTool()
    
    with patch('execution.tools.database_query_tool.DatabaseManager') as mock_db_mgr:
        instance = mock_db_mgr.return_value
        instance.async_session_maker = sqlite_db
        instance.close = AsyncMock()
        
        result = await tool._arun(
            query_type="invalid",
            filters={}
        )
        
        assert "error" in result
        assert "Unknown query_type" in result["error"]
