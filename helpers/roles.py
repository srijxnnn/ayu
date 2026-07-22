import discord

from ranks import RANK_ROLE_IDS, RANK_TO_ROLE


async def assign_rank_role(member: discord.Member, rank: str) -> discord.Role | None:
    role_id = RANK_TO_ROLE.get(rank)
    if not role_id:
        return None

    new_role = member.guild.get_role(role_id)
    if not new_role:
        return None

    roles_to_remove = [
        role for role in member.roles if role.id in RANK_ROLE_IDS and role.id != role_id
    ]
    if roles_to_remove:
        await member.remove_roles(*roles_to_remove, reason="cf rank update")

    if new_role not in member.roles:
        await member.add_roles(new_role, reason=f"cf rank set to {rank}")

    return new_role
