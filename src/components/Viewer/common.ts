export type VideoInfo = {
    title: string;
    duration: string;
    channel: string;
    chapters?: {
        start_time: number;
        end_time: number;
        title: string;
    }[];
    video: string;
    audio: string;
    captions?: string;
}