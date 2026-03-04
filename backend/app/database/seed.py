import asyncio

from sqlalchemy import select

from app.database.engine import async_session
from app.database.models import Casino, Slot


async def seed():
    async with async_session() as session:
        # Check if casinos already seeded
        result = await session.execute(select(Casino).limit(1))
        has_casinos = result.scalar() is not None

        if not has_casinos:
            # --- Casinos ---
            casinos = [
            Casino(
                name="PIN-UP",
                slug="pinup",
                logo_url="https://jogai.fun/img/pinup.png",
                description_pt="PIN-UP é uma das maiores plataformas de apostas e cassino online da América Latina. Oferece slots, jogos ao vivo, apostas esportivas e bônus generosos.",
                description_es="PIN-UP es una de las mayores plataformas de apuestas y casino online de América Latina.",
                min_deposit=20.00,
                min_deposits={"BRL": 20.0, "MXN": 400.0},
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
                min_deposits={"BRL": 10.0, "MXN": 200.0},
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
                name="BET365",
                slug="bet365",
                logo_url="https://jogai.fun/img/bet365.png",
                description_pt="Bet365 é a maior casa de apostas do mundo. Cobertura completa de esportes, cassino ao vivo e odds competitivas com saque rápido via PIX.",
                description_es="Bet365 es la mayor casa de apuestas del mundo. Cobertura completa de deportes, casino en vivo y cuotas competitivas.",
                min_deposit=20.00,
                min_deposits={"BRL": 20.0, "MXN": 350.0},
                pix_supported=True,
                spei_supported=True,
                crypto_supported=False,
                withdrawal_time="1-24h",
                affiliate_program="Bet365 Affiliates",
                affiliate_link_template="https://bet365.com/?ref={ref_id}&uid={user_id}",
                ref_id="jogai_11111",
                is_active=True,
                geo=["BR", "MX"],
            ),
            Casino(
                name="RIVALO",
                slug="rivalo",
                logo_url="https://jogai.fun/img/rivalo.png",
                description_pt="Rivalo é uma plataforma focada na América Latina com apostas esportivas, cassino e promoções exclusivas para o Brasil.",
                description_es="Rivalo es una plataforma enfocada en América Latina con apuestas deportivas, casino y promociones exclusivas.",
                min_deposit=15.00,
                min_deposits={"BRL": 15.0, "MXN": 300.0},
                pix_supported=True,
                spei_supported=True,
                crypto_supported=False,
                withdrawal_time="1-24h",
                affiliate_program="Rivalo Affiliates",
                affiliate_link_template="https://rivalo.com/?ref={ref_id}&uid={user_id}",
                ref_id="jogai_22222",
                is_active=True,
                geo=["BR", "MX"],
            ),
            ]
            session.add_all(casinos)
            await session.flush()
            print("Seeded 4 casinos.")

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
                    best_casino_id=casinos[0].id,
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
                    best_casino_id=casinos[1].id,
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
                    best_casino_id=casinos[0].id,
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
                    best_casino_id=casinos[2].id,
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
                    best_casino_id=casinos[1].id,
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
                    best_casino_id=casinos[2].id,
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
                    best_casino_id=casinos[3].id,
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
                    best_casino_id=casinos[0].id,
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
                    best_casino_id=casinos[0].id,
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
                    best_casino_id=casinos[1].id,
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
                    best_casino_id=casinos[3].id,
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
                    best_casino_id=casinos[1].id,
                    geo=["BR", "MX"],
                    source="manual",
                    source_id="hacksaw-wanted-dead-or-a-wild",
                ),
                ]
            session.add_all(slots)
            print("Seeded 12 slots.")

        await session.commit()
        print("Seed complete.")


if __name__ == "__main__":
    asyncio.run(seed())
