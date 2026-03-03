import {MetadataRoute} from 'next';
import {fetchCasinoSlugs} from '@/lib/api';
import {getGuideSlugs} from '@/data/guides';

const BASE_URL = 'https://jogai.fun';
const locales = ['pt-BR', 'es-MX'];

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const casinoSlugs = await fetchCasinoSlugs();
  const guideSlugs = getGuideSlugs();

  const entries: MetadataRoute.Sitemap = [];

  // Home pages
  for (const locale of locales) {
    entries.push({
      url: `${BASE_URL}/${locale}`,
      lastModified: new Date(),
      changeFrequency: 'daily',
      priority: 1,
    });
  }

  // Casino listing pages
  for (const locale of locales) {
    entries.push({
      url: `${BASE_URL}/${locale}/casinos`,
      lastModified: new Date(),
      changeFrequency: 'daily',
      priority: 0.9,
    });
  }

  // Casino detail pages
  for (const locale of locales) {
    for (const slug of casinoSlugs) {
      entries.push({
        url: `${BASE_URL}/${locale}/casinos/${slug}`,
        lastModified: new Date(),
        changeFrequency: 'weekly',
        priority: 0.8,
      });
    }
  }

  // Bonuses pages
  for (const locale of locales) {
    entries.push({
      url: `${BASE_URL}/${locale}/bonuses`,
      lastModified: new Date(),
      changeFrequency: 'daily',
      priority: 0.9,
    });
  }

  // Guides listing
  for (const locale of locales) {
    entries.push({
      url: `${BASE_URL}/${locale}/guides`,
      lastModified: new Date(),
      changeFrequency: 'weekly',
      priority: 0.7,
    });
  }

  // Guide detail pages
  for (const locale of locales) {
    for (const slug of guideSlugs) {
      entries.push({
        url: `${BASE_URL}/${locale}/guides/${slug}`,
        lastModified: new Date(),
        changeFrequency: 'monthly',
        priority: 0.6,
      });
    }
  }

  return entries;
}
