export type Clip = {
  start: number;
  end: number;
  fromChapter?: string;
};

export const formatSeconds = (seconds: number) => {
  const date = new Date(seconds * 1000);
  const fullString = date.toISOString().slice(11, 19);
  if (fullString.startsWith("00")) {
    return fullString.split(":").slice(1).join(":");
  }
  return fullString;
};