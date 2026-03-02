const LOCALE_CONFIG: Record<
  string,
  { symbol: string; decimalSep: string; thousandsSep: string }
> = {
  'pt-BR': { symbol: 'R$', decimalSep: ',', thousandsSep: '.' },
  'es-MX': { symbol: 'MX$', decimalSep: '.', thousandsSep: ',' },
};

export function formatCurrency(
  amount: number,
  locale: string = 'pt-BR',
): string {
  const config = LOCALE_CONFIG[locale] || LOCALE_CONFIG['pt-BR'];
  const isNegative = amount < 0;
  const abs = Math.abs(amount);
  const intPart = Math.floor(abs);
  const decPart = Math.round((abs - intPart) * 100)
    .toString()
    .padStart(2, '0');

  let intStr = intPart.toString();
  const result: string[] = [];
  for (let i = intStr.length - 1, count = 0; i >= 0; i--, count++) {
    if (count > 0 && count % 3 === 0) result.unshift(config.thousandsSep);
    result.unshift(intStr[i]);
  }
  intStr = result.join('');

  const formatted = `${config.symbol}${intStr}${config.decimalSep}${decPart}`;
  return isNegative ? `-${formatted}` : formatted;
}
