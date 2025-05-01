import translations from "../locales/fr-FR.json";

export function t(key: string): string {
  const keys = key.split(".");
  let translation: any = translations;

  for (const k of keys) {
    if (translation[k] === undefined) {
      console.warn(`Missing translation for key: ${key}`);
      return key;
    }
    translation = translation[k];
  }

  return translation;
}