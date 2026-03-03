export type Guide = {
  slug: string;
  titleKey: string;
  descriptionKey: string;
  contentKey: string;
  readTime: number;
};

export const guides: Guide[] = [
  {
    slug: 'como-funcionam-bonus',
    titleKey: 'guides_content.como-funcionam-bonus.title',
    descriptionKey: 'guides_content.como-funcionam-bonus.description',
    contentKey: 'guides_content.como-funcionam-bonus.content',
    readTime: 8,
  },
  {
    slug: 'o-que-e-wagering',
    titleKey: 'guides_content.o-que-e-wagering.title',
    descriptionKey: 'guides_content.o-que-e-wagering.description',
    contentKey: 'guides_content.o-que-e-wagering.content',
    readTime: 6,
  },
  {
    slug: 'jogai-score-como-funciona',
    titleKey: 'guides_content.jogai-score-como-funciona.title',
    descriptionKey: 'guides_content.jogai-score-como-funciona.description',
    contentKey: 'guides_content.jogai-score-como-funciona.content',
    readTime: 5,
  },
];

export function getGuideBySlug(slug: string): Guide | undefined {
  return guides.find((g) => g.slug === slug);
}

export function getGuideSlugs(): string[] {
  return guides.map((g) => g.slug);
}
