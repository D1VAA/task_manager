from typing import Dict, List, Any, Annotated, Optional

from dataclasses import dataclass
from database.crud_database import create_freight, query_freight, get_unique_values
from database.models import Freight
from .colors import Colors
