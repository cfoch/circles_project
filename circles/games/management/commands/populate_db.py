import os
import random
import datetime

from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.utils import timezone

from games.models import Color, Game, Sequence, Player, Payment


class Command(BaseCommand):
    args = '<foo bar ...>'
    help = 'our help string comes here'

    def _create_colors(self):
        print "Populating Colors"
        light_colors = (
            {"color":Color.RED,     "hex_code":"FF4D00"},
            {"color":Color.ORANGE,  "hex_code":"FF9A00"},
            {"color":Color.YELLOW,  "hex_code":"FFFC00"},
            {"color":Color.GREEN,   "hex_code":"58E20D"},
            {"color":Color.BLUE,    "hex_code":"164DFF"},
            {"color":Color.PURPLE,  "hex_code":"C900FF"},
        )
        dark_colors = (
            {"color":Color.RED,     "hex_code":"AB0000"},
            {"color":Color.ORANGE,  "hex_code":"CD6A00"},
            {"color":Color.YELLOW,  "hex_code":"FFB300"},
            {"color":Color.GREEN,   "hex_code":"5AA50E"},
            {"color":Color.BLUE,    "hex_code":"072B71"},
            {"color":Color.PURPLE,  "hex_code":"6C0771"},
        )
        for info in light_colors:
            color = Color(color=info["color"], hex_code=info["hex_code"], tonality=Color.LIGHT)
            color.save()

        for info in dark_colors:
            color = Color(color=info["color"], hex_code=info["hex_code"], tonality=Color.DARK)
            color.save()
        print "SUCCESS"

    def _create_games(self, n=1):
        if Color.objects.count() < Game.AVAILABLE_COLORS:
            print "Impossible to create games. No enough colors."
            print "ESCAPING..."
            return

        print "Populating Games"
        for i in range(n):
            available_colors = Color.objects.all().order_by('?')[:Game.AVAILABLE_COLORS]

            game = Game()
            game.initial_amount = random.randint(0, 100)
            game.percentage = random.randint(0, 100)
            game.payment = random.uniform(0, 5)
            game.start_date = timezone.now()
            game.end_date = game.start_date + datetime.timedelta(days=random.randint(3, 30))
            game.save()
            game.available_colors.add(*available_colors)
        print "SUCCESS"


    def _create_players(self):
        print "Populating players"
        emails_fname = "games/management/commands/data/emails.txt"
        with open(emails_fname) as f:
            emails = f.read().splitlines()

        for email in emails:
            player = Player()
            player.paypal = email
            player.save()

            # The play has played n-sequences in different games
            n = random.randint(1,10)
            for i in range(n):
                sequence = self._create_sequence()
                player.sequences.add(sequence)
                # Add the player to the current sequence
                sequence.players.add(player)
                sequence.save()

            # Generate payments
            for i in range(random.randint(0, 5)):
                payment = self._create_payment()
                player.payments.add(payment)

            player.save()
        print "SUCCESS"

    def _create_sequence(self):
        """
        Creates or get a sequence randomly.
        """
        game = Game.objects.all().order_by('?')[0]
        available_colors = list(game.available_colors.all())
        colors_randomized = [color for color in available_colors]
        random.shuffle(colors_randomized)
        print(colors_randomized)
        try:
            sequence = Sequence.objects.get(colors=colors_randomized)
        except:
            sequence = Sequence()
            sequence.save()
            sequence.colors.add(*colors_randomized)
            sequence.save()
        return sequence

    def _create_payment(self):
        """
        Creates a payment randomly, then returns it.
        """
        payment = Payment()
        payment.amount = random.uniform(0, 5)
        payment.quantity = random.randint(1, 5)
        payment.save()
        return payment

    def _reset_database(self):
        db_file = "db.sqlite3"
        if os.path.exists(db_file):
            os.remove(db_file)
        call_command('syncdb', interactive=True)
        

    def handle(self, *args, **options):
        self._reset_database()
        self._create_colors()
        self._create_games(3)
        self._create_players()
