from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.deps import get_locale
from app.i18n import t
from app.services.casino_matcher import match_casinos
from app.utils.formatters import format_currency

router = APIRouter(prefix="/quiz", tags=["quiz"])


class QuizAnswers(BaseModel):
    game_type: str = "slots"
    deposit_range: str = "medium"
    payment: str = "pix"
    priority: str = "bonus"
    experience: str = "beginner"
    geo: str = "BR"
    locale: str = "pt_BR"


class CasinoResult(BaseModel):
    name: str
    slug: str
    match_percent: int
    description: str
    min_deposit_formatted: str
    withdrawal_time: str
    best_bonus: str | None = None
    affiliate_link: str | None = None


@router.post("/start")
async def quiz_start(locale: str = Depends(get_locale)):
    """Return quiz questions with localized text."""
    questions = []
    for i in range(1, 6):
        q_key = f"casino_q{i}"
        question = {"question": t(q_key, locale), "options": []}

        # Collect options for this question
        option_keys = {
            1: ["slots", "crash", "sports", "table"],
            2: ["low", "medium", "high", "vip"],
            3: ["pix", "crypto", "card"],
            4: ["bonus", "wagering", "withdraw"],
            5: ["beginner", "intermediate", "advanced"],
        }
        for opt in option_keys[i]:
            opt_key = f"casino_q{i}_{opt}"
            question["options"].append({
                "value": opt,
                "label": t(opt_key, locale),
            })
        questions.append(question)

    return {"questions": questions}


@router.post("/result", response_model=list[CasinoResult])
async def quiz_result(body: QuizAnswers):
    locale = body.locale
    results = await match_casinos(
        geo=body.geo,
        game_type=body.game_type,
        deposit_range=body.deposit_range,
        payment=body.payment,
        priority=body.priority,
        experience=body.experience,
    )

    output = []
    for r in results:
        casino = r["casino"]
        suffix = "pt" if locale.startswith("pt") else "es"
        desc = getattr(casino, f"description_{suffix}", None) or casino.description_pt or ""

        best_bonus = None
        if casino.bonuses:
            best = max(casino.bonuses, key=lambda b: float(b.jogai_score or 0))
            best_bonus = getattr(best, f"title_{suffix}", None) or best.title_pt

        link = None
        if casino.affiliate_link_template:
            link = casino.affiliate_link_template.format(
                ref_id=casino.ref_id or "", user_id=0
            )

        output.append(CasinoResult(
            name=casino.name,
            slug=casino.slug,
            match_percent=r["match_percent"],
            description=desc,
            min_deposit_formatted=format_currency(casino.min_deposit or 0, locale),
            withdrawal_time=casino.withdrawal_time or "—",
            best_bonus=best_bonus,
            affiliate_link=link,
        ))

    return output
