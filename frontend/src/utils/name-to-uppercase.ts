export function nameToUpperCase(fullName: string) : string {
  return fullName.split(' ').map(subName => subName.charAt(0).toUpperCase() + subName.slice(1)).join(' ');
}