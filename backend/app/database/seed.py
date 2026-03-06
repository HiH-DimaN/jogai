import asyncio

from sqlalchemy import select

from app.database.engine import async_session
from app.database.models import Bonus, Casino, Slot


async def seed():
    async with async_session() as session:
        # Check if casinos already seeded
        result = await session.execute(select(Casino).limit(1))
        has_casinos = result.scalar() is not None

        if not has_casinos:
            # --- Casinos ---
            casinos = [
            # PIN-UP: MX only (no Brazil in PIN-UP Partners program)
            # RevShare 40%, waiting for tracking link from manager Nikita
            Casino(
                name="PIN-UP",
                slug="pinup",
                logo_url="https://jogai.fun/img/pinup.png",
                description_pt="PIN-UP é uma das maiores plataformas de apostas e cassino online da América Latina. Oferece slots, jogos ao vivo, apostas esportivas e bônus generosos.",
                description_es="PIN-UP es una de las mayores plataformas de apuestas y casino online de América Latina. Ofrece slots, juegos en vivo, apuestas deportivas y bonos generosos.",
                min_deposit=400.00,
                min_deposits={"MXN": 400.0},
                pix_supported=False,
                spei_supported=True,
                crypto_supported=True,
                withdrawal_time="1-24h",
                affiliate_program="PIN-UP Partners",
                affiliate_link_template="",  # Waiting for tracking link from manager
                ref_id="",
                is_active=True,
                geo=["MX"],
            ),
            # 1WIN: BR + MX — real tracking links received
            # Promo code: JOGAI
            Casino(
                name="1WIN",
                slug="1win",
                logo_url="https://jogai.fun/img/1win.png",
                description_pt="1WIN oferece mais de 10.000 slots, cassino ao vivo e apostas esportivas com odds competitivas. Saque rápido via PIX. Código promocional: JOGAI",
                description_es="1WIN ofrece más de 10,000 slots, casino en vivo y apuestas deportivas con cuotas competitivas. Código promocional: JOGAI",
                min_deposit=10.00,
                min_deposits={"BRL": 10.0, "MXN": 200.0},
                pix_supported=True,
                spei_supported=True,
                crypto_supported=True,
                withdrawal_time="1-12h",
                affiliate_program="1WIN Partners",
                # BR link: https://lkwn.cc/fd8e81, MX link: https://lkbz.cc/42546f
                affiliate_link_template="",  # Using direct links per geo on bonuses
                ref_id="",
                is_active=True,
                geo=["BR", "MX"],
            ),
            # Bet365: REMOVED — affiliate program rejected our application
            # Rivalo: REMOVED — DNS/Cloudflare broken, affiliate site unreachable
            # MX-specific casinos
            Casino(
                name="CALIENTE",
                slug="caliente",
                logo_url="https://jogai.fun/img/caliente.png",
                description_pt="Caliente é a maior casa de apostas do México, com licença federal e ampla cobertura de esportes e cassino online.",
                description_es="Caliente es la mayor casa de apuestas de México, con licencia federal y amplia cobertura de deportes y casino online.",
                min_deposit=200.00,
                min_deposits={"MXN": 200.0},
                pix_supported=False,
                spei_supported=True,
                crypto_supported=False,
                withdrawal_time="1-48h",
                affiliate_program="Caliente Affiliates",
                affiliate_link_template="https://caliente.mx/?ref={ref_id}&uid={user_id}",
                ref_id="jogai_33333",
                is_active=True,
                geo=["MX"],
            ),
            Casino(
                name="CODERE",
                slug="codere",
                logo_url="https://jogai.fun/img/codere.png",
                description_pt="Codere é uma operadora espanhola com forte presença no México, oferecendo apostas esportivas e cassino online com licença local.",
                description_es="Codere es una operadora española con fuerte presencia en México, ofreciendo apuestas deportivas y casino online con licencia local.",
                min_deposit=200.00,
                min_deposits={"MXN": 200.0},
                pix_supported=False,
                spei_supported=True,
                crypto_supported=False,
                withdrawal_time="1-24h",
                affiliate_program="Codere Affiliates",
                affiliate_link_template="https://codere.mx/?ref={ref_id}&uid={user_id}",
                ref_id="jogai_44444",
                is_active=True,
                geo=["MX"],
            ),
            ]
            session.add_all(casinos)
            await session.flush()
            print(f"Seeded {len(casinos)} casinos.")

        # Check if slots already seeded
        result = await session.execute(select(Slot).limit(1))
        has_slots = result.scalar() is not None

        if has_slots:
            print("Slots already seeded, skipping.")
        else:
            # Load casinos for FK references
            if has_casinos:
                result = await session.execute(select(Casino).order_by(Casino.id))
                casinos = list(result.scalars().all())

            # Build slug->casino map for FK references
            casino_map = {c.slug: c for c in casinos}

            # --- Slots (verified RTP from provider documentation) ---
            slots = [
                # Pragmatic Play
                Slot(
                    name="Gates of Olympus",
                    slug="gates-of-olympus",
                    provider="Pragmatic Play",
                    rtp=96.50,
                    volatility="high",
                    max_win="5000x",
                    reels=6,
                    lines=20,
                    features=["free spins", "multipliers", "tumble"],
                    tip_pt="Alta volatilidade — sessões longas sem prêmios são normais. Free spins ativam com 4+ Scatters. Aposte o mínimo até ativar o bônus.",
                    tip_es="Alta volatilidad — sesiones largas sin premios son normales. Free spins se activan con 4+ Scatters. Apuesta el mínimo hasta activar el bono.",
                    best_casino_id=casino_map["pinup"].id,
                    geo=["BR", "MX"],
                    source="manual",
                    source_id="pragmatic-gates-of-olympus",
                ),
                Slot(
                    name="Sweet Bonanza",
                    slug="sweet-bonanza",
                    provider="Pragmatic Play",
                    rtp=96.48,
                    volatility="high",
                    max_win="21175x",
                    reels=6,
                    lines=0,
                    features=["free spins", "multipliers", "tumble", "scatter pay"],
                    tip_pt="Multiplicadores acumulam nos free spins — é onde está o potencial. Sem linhas fixas, paga por cluster. Volatilidade alta exige paciência.",
                    tip_es="Los multiplicadores se acumulan en free spins — ahí está el potencial. Sin líneas fijas, paga por cluster. Volatilidad alta requiere paciencia.",
                    best_casino_id=casino_map["1win"].id,
                    geo=["BR", "MX"],
                    source="manual",
                    source_id="pragmatic-sweet-bonanza",
                ),
                Slot(
                    name="Big Bass Bonanza",
                    slug="big-bass-bonanza",
                    provider="Pragmatic Play",
                    rtp=96.71,
                    volatility="high",
                    max_win="2100x",
                    reels=5,
                    lines=10,
                    features=["free spins", "money collect", "wild"],
                    tip_pt="Fisherman Wild coleta valores dos símbolos de peixe. Free spins com 3+ Scatters. Jogo de volatilidade alta com potencial moderado.",
                    tip_es="Fisherman Wild recolecta valores de los símbolos de pez. Free spins con 3+ Scatters. Juego de alta volatilidad con potencial moderado.",
                    best_casino_id=casino_map["pinup"].id,
                    geo=["BR", "MX"],
                    source="manual",
                    source_id="pragmatic-big-bass-bonanza",
                ),
                Slot(
                    name="Wolf Gold",
                    slug="wolf-gold",
                    provider="Pragmatic Play",
                    rtp=96.01,
                    volatility="medium",
                    max_win="2500x",
                    reels=5,
                    lines=25,
                    features=["free spins", "money respin", "jackpot"],
                    tip_pt="Money Respin é a feature principal — 3 moons ativam respins com jackpots. Volatilidade média, sessões mais equilibradas.",
                    tip_es="Money Respin es la feature principal — 3 lunas activan respins con jackpots. Volatilidad media, sesiones más equilibradas.",
                    best_casino_id=casino_map["pinup"].id,
                    geo=["BR", "MX"],
                    source="manual",
                    source_id="pragmatic-wolf-gold",
                ),
                Slot(
                    name="The Dog House Megaways",
                    slug="the-dog-house-megaways",
                    provider="Pragmatic Play",
                    rtp=96.55,
                    volatility="high",
                    max_win="12305x",
                    reels=6,
                    lines=117649,
                    features=["free spins", "multipliers", "megaways", "sticky wilds"],
                    tip_pt="Sticky Wilds com multiplicadores nos free spins são a chave. Megaways = até 117.649 formas de ganhar. Volatilidade extrema.",
                    tip_es="Sticky Wilds con multiplicadores en free spins son la clave. Megaways = hasta 117,649 formas de ganar. Volatilidad extrema.",
                    best_casino_id=casino_map["1win"].id,
                    geo=["BR", "MX"],
                    source="manual",
                    source_id="pragmatic-dog-house-megaways",
                ),
                # NetEnt
                Slot(
                    name="Starburst",
                    slug="starburst",
                    provider="NetEnt",
                    rtp=96.09,
                    volatility="low",
                    max_win="500x",
                    reels=5,
                    lines=10,
                    features=["expanding wilds", "respins", "win both ways"],
                    tip_pt="Clássico de baixa volatilidade — ideal para cumprir wagering de bônus. Wilds expandem e dão respins. Ganhos frequentes mas pequenos.",
                    tip_es="Clásico de baja volatilidad — ideal para cumplir wagering de bonos. Wilds se expanden y dan respins. Ganancias frecuentes pero pequeñas.",
                    best_casino_id=casino_map["1win"].id,
                    geo=["BR", "MX"],
                    source="manual",
                    source_id="netent-starburst",
                ),
                Slot(
                    name="Gonzo's Quest",
                    slug="gonzos-quest",
                    provider="NetEnt",
                    rtp=95.97,
                    volatility="medium",
                    max_win="2500x",
                    reels=5,
                    lines=20,
                    features=["avalanche", "multipliers", "free falls"],
                    tip_pt="Sistema Avalanche: vitórias consecutivas aumentam o multiplicador (até 5x, 15x nos Free Falls). Volatilidade média-alta.",
                    tip_es="Sistema Avalanche: victorias consecutivas aumentan el multiplicador (hasta 5x, 15x en Free Falls). Volatilidad media-alta.",
                    best_casino_id=casino_map["pinup"].id,
                    geo=["BR", "MX"],
                    source="manual",
                    source_id="netent-gonzos-quest",
                ),
                Slot(
                    name="Dead or Alive 2",
                    slug="dead-or-alive-2",
                    provider="NetEnt",
                    rtp=96.80,
                    volatility="high",
                    max_win="111111x",
                    reels=5,
                    lines=9,
                    features=["free spins", "sticky wilds", "multipliers"],
                    tip_pt="Um dos slots mais voláteis do mercado. High Noon Saloon free spins pode dar ganhos enormes com sticky wilds. Espere muitas sessões secas.",
                    tip_es="Uno de los slots más volátiles del mercado. High Noon Saloon free spins puede dar ganancias enormes con sticky wilds. Espera muchas sesiones secas.",
                    best_casino_id=casino_map["pinup"].id,
                    geo=["BR", "MX"],
                    source="manual",
                    source_id="netent-dead-or-alive-2",
                ),
                # Play'n GO
                Slot(
                    name="Book of Dead",
                    slug="book-of-dead",
                    provider="Play'n GO",
                    rtp=96.21,
                    volatility="high",
                    max_win="5000x",
                    reels=5,
                    lines=10,
                    features=["free spins", "expanding symbol", "gamble"],
                    tip_pt="Nos free spins, um símbolo especial expande. Se cair o explorador (Rich Wilde), o potencial é máximo. Volatilidade alta, paciência necessária.",
                    tip_es="En free spins, un símbolo especial se expande. Si cae el explorador (Rich Wilde), el potencial es máximo. Volatilidad alta, paciencia necesaria.",
                    best_casino_id=casino_map["pinup"].id,
                    geo=["BR", "MX"],
                    source="manual",
                    source_id="playngo-book-of-dead",
                ),
                Slot(
                    name="Reactoonz",
                    slug="reactoonz",
                    provider="Play'n GO",
                    rtp=96.51,
                    volatility="high",
                    max_win="4570x",
                    reels=7,
                    lines=0,
                    features=["cluster pays", "cascading", "quantum features"],
                    tip_pt="Grid 7x7 com cluster pays. Quantum Features ativam aleatoriamente. Gargantoon (wild 3x3) é o grande prêmio. Volátil mas divertido.",
                    tip_es="Grid 7x7 con cluster pays. Quantum Features se activan aleatoriamente. Gargantoon (wild 3x3) es el gran premio. Volátil pero divertido.",
                    best_casino_id=casino_map["1win"].id,
                    geo=["BR", "MX"],
                    source="manual",
                    source_id="playngo-reactoonz",
                ),
                Slot(
                    name="Fire Joker",
                    slug="fire-joker",
                    provider="Play'n GO",
                    rtp=96.15,
                    volatility="low",
                    max_win="800x",
                    reels=3,
                    lines=5,
                    features=["respin", "multiplier wheel"],
                    tip_pt="Slot clássico 3x3 simples. Respin de Fogo quando 2 colunas são iguais. Wheel of Multipliers com até 10x. Baixa volatilidade, bom para iniciantes.",
                    tip_es="Slot clásico 3x3 simple. Respin de Fuego cuando 2 columnas son iguales. Wheel of Multipliers con hasta 10x. Baja volatilidad, bueno para principiantes.",
                    best_casino_id=casino_map["1win"].id,
                    geo=["BR", "MX"],
                    source="manual",
                    source_id="playngo-fire-joker",
                ),
                # Hacksaw Gaming
                Slot(
                    name="Wanted Dead or a Wild",
                    slug="wanted-dead-or-a-wild",
                    provider="Hacksaw Gaming",
                    rtp=96.38,
                    volatility="high",
                    max_win="12500x",
                    reels=5,
                    lines=10,
                    features=["free spins", "duel", "multiplier wilds", "versus"],
                    tip_pt="Duels entre personagens com multiplicadores crescentes. Free spins podem ser épicos ou zero. Volatilidade extrema — gerencie seu bankroll.",
                    tip_es="Duelos entre personajes con multiplicadores crecientes. Free spins pueden ser épicos o cero. Volatilidad extrema — gestiona tu bankroll.",
                    best_casino_id=casino_map["1win"].id,
                    geo=["BR", "MX"],
                    source="manual",
                    source_id="hacksaw-wanted-dead-or-a-wild",
                ),
            ]
            session.add_all(slots)
            print("Seeded 12 slots.")

        # --- Bonuses (VERIFIED from official sites and review sources, March 2026) ---
        result = await session.execute(select(Bonus).limit(1))
        has_bonuses = result.scalar() is not None

        if has_bonuses:
            print("Bonuses already seeded, skipping.")
        else:
            # Load casinos for FK references
            result = await session.execute(select(Casino))
            casino_map = {c.slug: c for c in result.scalars().all()}

            from datetime import datetime, timedelta
            from app.services.bonus_analyzer import calculate_jogai_score

            now = datetime.utcnow()
            expires = now + timedelta(days=90)

            # VERIFIED bonus data — sources cited in comments
            bonus_defs = [
                # --- BR bonuses ---
                # PIN-UP BR: REMOVED — PIN-UP Partners has no Brazil geo
                # Bet365 BR: REMOVED — affiliate program rejected
                # Rivalo BR: REMOVED — DNS broken, affiliate unreachable

                # Source: sportytrader.com, 1win.br.com (March 2026)
                # 500% across 4 deposits (100%+120%+130%+150%)
                # Up to ~R$7,000, wagering x50 for casino
                # 70 free spins, promo code: JOGAI
                {
                    "casino_slug": "1win",
                    "title_pt": "1WIN: 500% até R$7.000 nos 4 primeiros depósitos + 70 FS (código: JOGAI)",
                    "title_es": "1WIN: 500% hasta R$7,000 en los 4 primeros depósitos + 70 FS (código: JOGAI)",
                    "bonus_percent": 500,
                    "max_bonus_amount": 7000.0,
                    "max_bonus_currency": "BRL",
                    "wagering_multiplier": 50.0,
                    "wagering_deadline_days": 30,
                    "max_bet": 25.0,
                    "free_spins": 70,
                    "no_deposit": False,
                    "geo": ["BR"],
                    "affiliate_link": "https://lkwn.cc/fd8e81",
                },

                # --- MX bonuses ---
                # Source: pinupcassinos.com.br (same international offer applies to MX)
                # PIN-UP MX: RevShare 40%, waiting for tracking link from manager
                {
                    "casino_slug": "pinup",
                    "title_pt": "PIN-UP MX: 120% no primeiro depósito + 250 Free Spins",
                    "title_es": "PIN-UP MX: 120% en el primer depósito + 250 Free Spins",
                    "bonus_percent": 120,
                    "max_bonus_amount": 30000.0,
                    "max_bonus_currency": "MXN",
                    "wagering_multiplier": 20.0,
                    "wagering_deadline_days": 3,
                    "max_bet": 500.0,
                    "free_spins": 250,
                    "no_deposit": False,
                    "geo": ["MX"],
                    "affiliate_link": "",  # Waiting for PIN-UP Partners tracking link
                },
                # Source: sportytrader.com (same international offer for MX)
                # Promo code: JOGAI
                {
                    "casino_slug": "1win",
                    "title_pt": "1WIN MX: 500% nos 4 primeiros depósitos + 70 FS (código: JOGAI)",
                    "title_es": "1WIN MX: 500% en los 4 primeros depósitos + 70 FS (código: JOGAI)",
                    "bonus_percent": 500,
                    "max_bonus_amount": 60000.0,
                    "max_bonus_currency": "MXN",
                    "wagering_multiplier": 50.0,
                    "wagering_deadline_days": 30,
                    "max_bet": 400.0,
                    "free_spins": 70,
                    "no_deposit": False,
                    "geo": ["MX"],
                    "affiliate_link": "https://lkbz.cc/42546f",
                },
                # Source: legalbet.mx, caliente.mx (March 2026)
                # No-deposit: MX$1,000 registration bonus, wagering x40, 30 days
                {
                    "casino_slug": "caliente",
                    "title_pt": "Caliente: MX$1.000 sem depósito ao se registrar",
                    "title_es": "Caliente: MX$1,000 sin depósito al registrarte",
                    "bonus_percent": 0,
                    "max_bonus_amount": 1000.0,
                    "max_bonus_currency": "MXN",
                    "wagering_multiplier": 40.0,
                    "wagering_deadline_days": 30,
                    "max_bet": 200.0,
                    "free_spins": 0,
                    "no_deposit": True,
                    "geo": ["MX"],
                },
                # Source: legalbet.mx (March 2026)
                # Deposit bonus: 100-150% up to MX$20,000, wagering x20, 7 days
                {
                    "casino_slug": "caliente",
                    "title_pt": "Caliente: 100-150% até MX$20.000 no depósito",
                    "title_es": "Caliente: 100-150% hasta MX$20,000 en depósito",
                    "bonus_percent": 100,
                    "max_bonus_amount": 20000.0,
                    "max_bonus_currency": "MXN",
                    "wagering_multiplier": 20.0,
                    "wagering_deadline_days": 7,
                    "max_bet": 500.0,
                    "free_spins": 0,
                    "no_deposit": False,
                    "geo": ["MX"],
                },
                # Source: codere.mx, sportytrader.com, legalbet.mx (March 2026)
                # No-deposit: MX$1,000 for registration + 5 FS
                {
                    "casino_slug": "codere",
                    "title_pt": "Codere: MX$1.000 sem depósito + 5 Free Spins",
                    "title_es": "Codere: MX$1,000 sin depósito + 5 Free Spins",
                    "bonus_percent": 0,
                    "max_bonus_amount": 1000.0,
                    "max_bonus_currency": "MXN",
                    "wagering_multiplier": 30.0,
                    "wagering_deadline_days": 14,
                    "max_bet": 200.0,
                    "free_spins": 5,
                    "no_deposit": True,
                    "geo": ["MX"],
                },
                # Source: codere.mx, legalbet.mx (March 2026)
                # Casino deposit: up to MX$5,000 across 3 deposits (100%/50%/70%), x30, 14 days
                {
                    "casino_slug": "codere",
                    "title_pt": "Codere: Até MX$5.000 em 3 depósitos (100%/50%/70%)",
                    "title_es": "Codere: Hasta MX$5,000 en 3 depósitos (100%/50%/70%)",
                    "bonus_percent": 100,
                    "max_bonus_amount": 5000.0,
                    "max_bonus_currency": "MXN",
                    "wagering_multiplier": 30.0,
                    "wagering_deadline_days": 14,
                    "max_bet": 400.0,
                    "free_spins": 0,
                    "no_deposit": False,
                    "geo": ["MX"],
                },
            ]

            bonuses = []
            for bd in bonus_defs:
                casino = casino_map.get(bd["casino_slug"])
                if not casino:
                    print(f"Casino {bd['casino_slug']} not found, skipping bonus")
                    continue

                # Calculate Jogai Score
                deposit = 100.0 if bd["max_bonus_currency"] == "BRL" else 2000.0
                # For no-deposit bonuses, deposit is 0
                if bd["no_deposit"]:
                    deposit = 0.0

                score_result = calculate_jogai_score(
                    bonus_percent=bd["bonus_percent"] if bd["bonus_percent"] > 0 else 100,
                    wagering_multiplier=bd["wagering_multiplier"],
                    deadline_days=bd["wagering_deadline_days"],
                    max_bet=bd["max_bet"],
                    deposit=deposit if deposit > 0 else 100.0,
                    free_spins=bd["free_spins"],
                    no_deposit=bd["no_deposit"],
                )

                # Use direct affiliate link from bonus def, or generate from template
                affiliate_link = bd.get("affiliate_link")
                if affiliate_link is None and casino.affiliate_link_template:
                    affiliate_link = casino.affiliate_link_template.format(
                        ref_id=casino.ref_id or "", user_id=""
                    )

                bonuses.append(Bonus(
                    casino_id=casino.id,
                    title_pt=bd["title_pt"],
                    title_es=bd["title_es"],
                    bonus_percent=bd["bonus_percent"],
                    max_bonus_amount=bd["max_bonus_amount"],
                    max_bonus_currency=bd["max_bonus_currency"],
                    wagering_multiplier=bd["wagering_multiplier"],
                    wagering_deadline_days=bd["wagering_deadline_days"],
                    max_bet=bd["max_bet"],
                    free_spins=bd["free_spins"],
                    no_deposit=bd["no_deposit"],
                    jogai_score=score_result["jogai_score"],
                    verdict_key=score_result["verdict_key"],
                    expected_loss=score_result["expected_loss"],
                    profit_probability=score_result["profit_probability"],
                    affiliate_link=affiliate_link,
                    is_active=True,
                    starts_at=now,
                    expires_at=expires,
                    geo=bd["geo"],
                ))

            session.add_all(bonuses)
            print(f"Seeded {len(bonuses)} bonuses.")

        await session.commit()
        print("Seed complete.")


if __name__ == "__main__":
    asyncio.run(seed())
