from pathlib import Path


class RangeStream:

    CHUNK_SIZE = 64 * 1024     #64MB

    @staticmethod
    def parse_range(
        header: str | None,
        file_size: int,
    ):

        if not header:
            return (
                0,
                file_size - 1,
            )

        units, value = header.split("=")

        start, end = value.split("-")

        start = int(start)

        end = (
            int(end)
            if end
            else file_size - 1
        )

        print(f"header - {header}")

        print(f"value - {value}")

        print(f"{start} - {end}")

        return (
            start,
            end,
        )

    @staticmethod
    def stream(
        path: Path,
        start: int,
        end: int,
    ):

        with open(
            path,
            "rb",
        ) as file:

            file.seek(start)

            remaining = (
                end
                - start
                + 1
            )

            while remaining > 0:

                size = min(
                    RangeStream.CHUNK_SIZE,
                    remaining,
                )

                data = file.read(size)

                if not data:
                    break

                remaining -= len(data)

                yield data