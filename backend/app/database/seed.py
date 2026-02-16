import asyncio
from datetime import datetime, timedelta

from sqlalchemy import select

from app.database.engine import async_session
from app.database.models import Bonus, Casino, SportPick


async def seed():
    async with async_session() as session:
        # Check if already seeded
        result = await session.execute(select(Casino).limit(1))
        if result.scalar():
            print("Database already seeded, skipping.")
            return

        # --- Casinos ---
        casinos = [
            Casino(
                name="PIN-UP",
                slug="pinup",
                logo_url="https://jogai.fun/img/pinup.png",
                description_pt="PIN-UP é uma das maiores plataformas de apostas e cassino online da América Latina. Oferece slots, jogos ao vivo, apostas esportivas e bônus generosos.",
                description_es="PIN-UP es una de las mayores plataformas de apuestas y casino online de América Latina.",
                min_deposit=20.00,
                pix_supported=True,
                spei_supported=True,
                crypto_supported=True,
                withdrawal_time="1-24h",
                affiliate_program="PIN-UP Partners",
                affiliate_link_template="https://pinup.com/?ref={ref_id}&uid={user_id}",
                ref_id="jogai_12345",
                is_active=True,
                geo=["BR", "MX"],
            ),
            Casino(
                name="1WIN",
                slug="1win",
                logo_url="https://jogai.fun/img/1win.png",
                description_pt="1WIN oferece mais de 10.000 slots, cassino ao vivo e apostas esportivas com odds competitivas. Saque rápido via PIX.",
                description_es="1WIN ofrece más de 10,000 slots, casino en vivo y apuestas deportivas con cuotas competitivas.",
                min_deposit=10.00,
                pix_supported=True,
                spei_supported=True,
                crypto_supported=True,
                withdrawal_time="1-12h",
                affiliate_program="1WIN Partners",
                affiliate_link_template="https://1win.com/?ref={ref_id}&uid={user_id}",
                ref_id="jogai_67890",
                is_active=True,
                geo=["BR", "MX"],
            ),
            Casino(
                name="STARDA",
                slug="starda",
                logo_url="https://jogai.fun/img/starda.png",
                description_pt="STARDA Casino é especializado em slots e crash games com bônus de boas-vindas agressivo e wagering baixo.",
                description_es="STARDA Casino se especializa en slots y crash games con bono de bienvenida agresivo.",
                min_deposit=30.00,
                pix_supported=True,
                spei_supported=False,
                crypto_supported=True,
                withdrawal_time="1-48h",
                affiliate_program="STARDA Affiliates",
                affiliate_link_template="https://starda.com/?ref={ref_id}&uid={user_id}",
                ref_id="jogai_11111",
                is_active=True,
                geo=["BR"],
            ),
        ]
        session.add_all(casinos)
        await session.flush()

        # --- Bonuses ---
        now = datetime.utcnow()
        bonuses = [
            Bonus(
                casino_id=casinos[0].id,
                title_pt="Bônus de Boas-Vindas 150% até R$1.500",
                title_es="Bono de Bienvenida 150% hasta MX$5,000",
                bonus_percent=150,
                max_bonus_amount=1500.00,
                max_bonus_currency="BRL",
                wagering_multiplier=35.0,
                wagering_deadline_days=30,
                max_bet=25.00,
                free_spins=250,
                jogai_score=8.5,
                verdict_key="verdict_excellent",
                expected_loss=350.00,
                profit_probability=32.00,
                affiliate_link="https://pinup.com/?ref=jogai_12345",
                is_active=True,
                starts_at=now,
                expires_at=now + timedelta(days=30),
                geo=["BR"],
            ),
            Bonus(
                casino_id=casinos[0].id,
                title_pt="Sexta Sem Risco — Cashback 10%",
                title_es="Viernes Sin Riesgo — Cashback 10%",
                bonus_percent=10,
                max_bonus_amount=500.00,
                max_bonus_currency="BRL",
                wagering_multiplier=5.0,
                wagering_deadline_days=7,
                max_bet=50.00,
                jogai_score=7.2,
                verdict_key="verdict_good",
                expected_loss=50.00,
                profit_probability=65.00,
                affiliate_link="https://pinup.com/?ref=jogai_12345",
                is_active=True,
                starts_at=now,
                expires_at=now + timedelta(days=7),
                geo=["BR"],
            ),
            Bonus(
                casino_id=casinos[1].id,
                title_pt="1WIN: 500% no primeiro depósito",
                title_es="1WIN: 500% en el primer depósito",
                bonus_percent=500,
                max_bonus_amount=5000.00,
                max_bonus_currency="BRL",
                wagering_multiplier=50.0,
                wagering_deadline_days=30,
                max_bet=15.00,
                jogai_score=5.0,
                verdict_key="verdict_caution",
                expected_loss=2800.00,
                profit_probability=12.00,
                affiliate_link="https://1win.com/?ref=jogai_67890",
                is_active=True,
                starts_at=now,
                expires_at=now + timedelta(days=60),
                geo=["BR"],
            ),
            Bonus(
                casino_id=casinos[1].id,
                title_pt="Rodadas Grátis — 70 Free Spins sem depósito",
                title_es="Giros Gratis — 70 Free Spins sin depósito",
                bonus_percent=0,
                max_bonus_amount=0,
                max_bonus_currency="BRL",
                wagering_multiplier=40.0,
                wagering_deadline_days=7,
                max_bet=5.00,
                free_spins=70,
                no_deposit=True,
                jogai_score=6.8,
                verdict_key="verdict_good",
                expected_loss=0,
                profit_probability=18.00,
                affiliate_link="https://1win.com/?ref=jogai_67890",
                is_active=True,
                starts_at=now,
                expires_at=now + timedelta(days=14),
                geo=["BR"],
            ),
            Bonus(
                casino_id=casinos[2].id,
                title_pt="STARDA: 100% + 100 FS — Wagering x25",
                title_es="STARDA: 100% + 100 FS — Wagering x25",
                bonus_percent=100,
                max_bonus_amount=2000.00,
                max_bonus_currency="BRL",
                wagering_multiplier=25.0,
                wagering_deadline_days=14,
                max_bet=30.00,
                free_spins=100,
                jogai_score=9.1,
                verdict_key="verdict_excellent",
                expected_loss=200.00,
                profit_probability=45.00,
                affiliate_link="https://starda.com/?ref=jogai_11111",
                is_active=True,
                starts_at=now,
                expires_at=now + timedelta(days=30),
                geo=["BR"],
            ),
            Bonus(
                casino_id=casinos[2].id,
                title_pt="STARDA Reload: 50% toda segunda",
                title_es="STARDA Reload: 50% cada lunes",
                bonus_percent=50,
                max_bonus_amount=1000.00,
                max_bonus_currency="BRL",
                wagering_multiplier=30.0,
                wagering_deadline_days=7,
                max_bet=20.00,
                jogai_score=3.5,
                verdict_key="verdict_bad",
                expected_loss=600.00,
                profit_probability=8.00,
                affiliate_link="https://starda.com/?ref=jogai_11111",
                is_active=True,
                starts_at=now,
                expires_at=now + timedelta(days=7),
                geo=["BR"],
            ),
        ]
        session.add_all(bonuses)

        # --- Sport Pick ---
        sport_pick = SportPick(
            match_name="Flamengo vs Palmeiras",
            league="Brasileirão Série A",
            pick_description_pt="Flamengo em casa com elenco completo. Odds com valor no empate.",
            pick_description_es="Flamengo en casa con plantel completo. Cuotas con valor en empate.",
            odds=3.20,
            analysis_pt="Flamengo domina em casa (78% aproveitamento). Palmeiras sem 2 titulares. Histórico: últimos 5 jogos em casa — 4V 1E 0D. Recomendação: Empate ou Flamengo (Dupla Chance).",
            analysis_es="Flamengo domina en casa (78% aprovechamiento). Palmeiras sin 2 titulares.",
            casino_id=casinos[0].id,
            affiliate_link="https://pinup.com/?ref=jogai_12345",
            match_date=now + timedelta(days=1),
            geo=["BR"],
        )
        session.add(sport_pick)

        await session.commit()
        print("Seed complete: 3 casinos, 6 bonuses, 1 sport_pick")


if __name__ == "__main__":
    asyncio.run(seed())
