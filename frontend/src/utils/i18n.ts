import translations from "../locales/fr-FR.json";

export function t(key: string): string {
  const keys = key.split(".");
  let translation: unknown = translations;

  for (const k of keys) {
    if (
      typeof translation !== "object" ||
      translation === null ||
      !(k in translation)
    ) {
      console.warn(`Missing translation for key: ${key}`);
      return key;
    }
    translation = (translation as Record<string, unknown>)[k];
  }

  if (typeof translation === "string") {
    return translation;
  } else {
    console.warn(`Translation for key "${key}" is not a string`);
    return key;
  }
}
