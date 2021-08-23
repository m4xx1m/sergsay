from typing import Tuple
from requests import get
from loguru import logger
from os import close, remove
from sys import stdout, executable, modules


# emulate print("abc", end="")
def formatter(record):
    end = record["extra"].get("end", "\n")
    return "<green>{time:YYYY-MM-DD HH:mm:ss}</green> <red>|</red> <cyan>{level}</cyan> <red>|</red> <bold>{message}</bold>" + end


logger.remove()
logger.add(stdout, format=formatter)
API_LINK = "https://nextup.com/ivona/php/nextup-polly/CreateSpeech/CreateSpeechGet3.php?voice=Maxim&language=ru-RU&text={text}"


def _api_request(text: str) -> Tuple[int, str]:
    _req = get(API_LINK.format(text=text))
    return _req.status_code, _req.content.decode('utf-8')


def main():
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument("-t", "--text", required=True, help="Text in quotes")
    parser.add_argument("-s", "--save", default=None, help="Save audiofile to <path>")
    parser.add_argument("-p", "--play", default=None, action="store_true", help="Play sound")
    args = parser.parse_args()
    del ArgumentParser, parser

    logger.info("Making API request")
    exit_code, link = _api_request(args.text)
    if exit_code != 200:
        logger.error(f'Error while making api request (code: {exit_code}): {link}')
        exit(-1)
    logger.info("Api request successful")
    logger.info(f"Link to sound: {link}")

    if args.save or args.play:
        file_content = get(link, stream=True).content

    if args.save:
        # logger.info("Saving")
        with open(args.save, "wb") as _sound_file:
            _sound_file.write(file_content)

        logger.info(f"Sound saved to {args.save}")

    if args.play:
        from tempfile import mkstemp
        try:
            from playsound import playsound
        except ModuleNotFoundError:
            logger.bind(end="").warning("playsound doesn't found. Are you want to install? (Y/n) - ")
            if input("").lower() in ['', 'y']:
                if "pip" not in modules:
                    logger.error("Pip not found")
                    exit(-1)

                logger.info("Installing playsound")
                from subprocess import Popen, PIPE
                _proc = Popen(
                    [executable, '-m', 'pip', 'install', 'playsound'],
                    stdout=PIPE,
                    stderr=PIPE
                )
                del Popen, PIPE
                _proc.wait()
                if _proc.returncode == 0:
                    logger.info("Playsound installed successfully")
                else:
                    logger.error("Error installing playsound. Try to install manually")
                    exit(-1)

        fd, tempPath = mkstemp(prefix='PS', suffix=".mp3")
        with open(tempPath, "wb") as _tempfile:
            _tempfile.write(file_content)
        close(fd)
        logger.info("Playing")
        playsound(tempPath)
        remove(tempPath)


if __name__ == '__main__':
    logger.info("Initializing")
    main()
