"""Promo codes tools for Pokemon Go MCP server."""

import logging
from typing import List
from datetime import datetime

from .api_client import api_client
from .types import PromoCodeInfo
from .utils import get_current_time_str, format_json_output

logger = logging.getLogger(__name__)


def register_promo_code_tools(mcp):
    """Register promo code related tools with the MCP server."""
    
    @mcp.tool()
    async def get_active_promo_codes() -> str:
        """Get all currently active promo codes with their rewards and expiration dates.
        
        Returns a formatted list of active promo codes that can be redeemed in Pokemon GO,
        including their rewards, descriptions, and expiration information.
        """
        try:
            logger.info("Fetching active promo codes...")
            promo_codes = await api_client.get_promo_codes()
            
            if not promo_codes:
                return "No active promo codes found."
            
            result = f"# 🎁 Active Pokemon GO Promo Codes ({get_current_time_str()})\n\n"
            result += f"**Total Active Codes:** {len(promo_codes)}\n\n"
            
            for code in promo_codes:
                result += f"## **{code.code}**\n"
                result += f"**{code.title}**\n\n"
                result += f"{code.description}\n\n"
                
                # Rewards
                if code.rewards:
                    result += "**Rewards:**\n"
                    for reward in code.rewards:
                        result += f"• {reward.name}\n"
                    result += "\n"
                
                # Expiration
                if code.expiration:
                    try:
                        # Parse expiration date
                        exp_date = datetime.fromisoformat(code.expiration.replace('Z', '+00:00'))
                        result += f"**Expires:** {exp_date.strftime('%B %d, %Y at %I:%M %p %Z')}\n"
                    except Exception:
                        result += f"**Expires:** {code.expiration}\n"
                
                # Redemption link
                result += f"\n[Redeem Code]({code.redemption_url})\n\n"
                result += "---\n\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Error fetching promo codes: {e}")
            return f"Error fetching promo codes: {str(e)}"