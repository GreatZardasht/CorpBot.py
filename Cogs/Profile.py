import asyncio
import discord
import time
from   operator import itemgetter
from   discord.ext import commands
from   Cogs import Settings
from   Cogs import ReadableTime
from   Cogs import DisplayName
from   Cogs import Nullify

# This is the profiles module.

class Profile:

	# Init with the bot reference, and a reference to the settings var
	def __init__(self, bot, settings):
		self.bot = bot
		self.settings = settings

		
	@commands.command(pass_context=True)
	async def addprofile(self, ctx, name : str = None, *, link : str = None):
		"""Add a profile to your profile list."""

		# Check if we're suppressing @here and @everyone mentions
		if self.settings.getServerStat(ctx.message.server, "SuppressMentions").lower() == "yes":
			suppress = True
		else:
			suppress = False
		
		channel = ctx.message.channel
		author  = ctx.message.author
		server  = ctx.message.server
		
		# Check for role requirements
		requiredRole = self.settings.getServerStat(server, "RequiredXPRole")
		if requiredRole == "":
			#admin only
			isAdmin = author.permissions_in(channel).administrator
			if not isAdmin:
				await self.bot.send_message(channel, 'You do not have sufficient privileges to access this command.')
				return
		else:
			#role requirement
			hasPerms = False
			for role in author.roles:
				if role.id == requiredRole:
					hasPerms = True
			if not hasPerms:
				await self.bot.send_message(channel, 'You do not have sufficient privileges to access this command.')
				return
				
		# Passed role requirements!
		if not (name or link):
			msg = 'Usage: `{}addprofile "[profile name]" [link]`'.format(ctx.prefix)
			await self.bot.send_message(channel, msg)
			return

		linkList = self.settings.getUserStat(author, server, "Profiles")
		if not linkList:
			linkList = []
		
		found = False
		currentTime = int(time.time())	
		for alink in linkList:
			if alink['Name'].lower() == name.lower():
				# The link exists!
				msg = '*{}\'s* *{}* profile was updated!'.format(DisplayName.name(author), name)
				# Check for suppress
				if suppress:
					msg = Nullify.clean(msg)
				alink['URL'] = link
				alink['Updated'] = currentTime
				found = True
		if not found:	
			linkList.append({"Name" : name, "URL" : link, "Created" : currentTime})
			msg = '*{}* added to *{}\'s* profile list!'.format(name, DisplayName.name(author))
			# Check for suppress
			if suppress:
				msg = Nullify.clean(msg)
		
		self.settings.setUserStat(author, server, "Profiles", linkList)
		await self.bot.send_message(channel, msg)
		
		
	@commands.command(pass_context=True)
	async def removeprofile(self, ctx, *, name : str = None):
		"""Remove a profile from your profile list."""
		
		channel = ctx.message.channel
		author  = ctx.message.author
		server  = ctx.message.server

		# Check if we're suppressing @here and @everyone mentions
		if self.settings.getServerStat(ctx.message.server, "SuppressMentions").lower() == "yes":
			suppress = True
		else:
			suppress = False
		
		# Check for role requirements
		requiredRole = self.settings.getServerStat(server, "RequiredXPRole")
		if requiredRole == "":
			#admin only
			isAdmin = author.permissions_in(channel).administrator
			if not isAdmin:
				await self.bot.send_message(channel, 'You do not have sufficient privileges to access this command.')
				return
		else:
			#role requirement
			hasPerms = False
			for role in author.roles:
				if role.id == requiredRole:
					hasPerms = True
			if not hasPerms:
				await self.bot.send_message(channel, 'You do not have sufficient privileges to access this command.')
				return
		
		if name == None:
			msg = 'Usage: `{}removeprofile "[profile name]"`'.format(ctx.prefix)
			await self.bot.send_message(channel, msg)
			return

		linkList = self.settings.getUserStat(author, server, "Profiles")
		if not linkList or linkList == []:
			msg = '*{}* has no profiles set!  They can add some with the `{}addprofile "[profile name]" [url]` command!'.format(DisplayName.name(author), ctx.prefix)
			await self.bot.send_message(channel, msg)
			return

		for alink in linkList:
			if alink['Name'].lower() == name.lower():
				linkList.remove(alink)
				self.settings.setUserStat(author, server, "Profiles", linkList)
				msg = '*{}* removed from *{}\'s* profile list!'.format(alink['Name'], DisplayName.name(author))
				# Check for suppress
				if suppress:
					msg = Nullify.clean(msg)
				await self.bot.send_message(channel, msg)
				return

		msg = '*{}* not found in *{}\'s* profile list!'.format(name, DisplayName.name(author))
		# Check for suppress
		if suppress:
			msg = Nullify.clean(msg)
		await self.bot.send_message(channel, msg)


	@commands.command(pass_context=True)
	async def profile(self, ctx, *, member : str = None, name : str = None):
		"""Retrieve a profile from the passed user's profile list."""
		
		channel = ctx.message.channel
		author  = ctx.message.author
		server  = ctx.message.server

		# Check if we're suppressing @here and @everyone mentions
		if self.settings.getServerStat(ctx.message.server, "SuppressMentions").lower() == "yes":
			suppress = True
		else:
			suppress = False
		
		if not member:
			msg = 'Usage: `{}profile [member] [profile name]`'.format(ctx.prefix)
			await self.bot.send_message(channel, msg)
			return

		# name is likely to be empty unless quotes are used
		if name == None:
			# Either a name wasn't set - or it's the last section
			if type(member) is str:
				# It' a string - the hope continues
				# Let's search for a name at the beginning - and a profile at the end
				parts = member.split()
				for j in range(len(parts)):
					# Reverse search direction
					i = len(parts)-1-j
					memFromName = None
					foundProf   = False
					# Name = 0 up to i joined by space
					nameStr    = ' '.join(parts[0:i+1])
					# Profile = end of name -> end of parts joined by space
					profileStr = ' '.join(parts[i+1:])
					memFromName = DisplayName.memberForName(nameStr, ctx.message.server)
					if memFromName:
						# We got a member - let's check for a profile
						linkList = self.settings.getUserStat(memFromName, server, "Profiles")
						if not linkList or linkList == []:
							pass

						for alink in linkList:
							if alink['Name'].lower() == profileStr.lower():
								# Found the link - return it.
								msg = '*{}\'s {} Profile:*\n\n{}'.format(DisplayName.name(memFromName), alink['Name'], alink['URL'])
								# Check for suppress
								if suppress:
									msg = Nullify.clean(msg)
								await self.bot.send_message(channel, msg)
								return
		# Check if there is no member specified
		linkList = self.settings.getUserStat(author, server, "Profiles")
		if not linkList or linkList == []:
			pass

		for alink in linkList:
			if alink['Name'].lower() == member.lower():
				# Found the link - return it.
				msg = '*{}\'s {} Profile:*\n\n{}'.format(DisplayName.name(author), alink['Name'], alink['URL'])
				# Check for suppress
				if suppress:
					msg = Nullify.clean(msg)
				await self.bot.send_message(channel, msg)
				return

		# If we got this far - we didn't find them or somehow they added a name
		msg = 'Sorry, I couldn\'t find that user/profile.'
		await self.bot.send_message(channel, msg)
			

	@commands.command(pass_context=True)
	async def profileinfo(self, ctx, *, member : str = None, name : str = None):
		"""Displays info about a profile from the passed user's profile list."""

		channel = ctx.message.channel
		author  = ctx.message.author
		server  = ctx.message.server

		# Check if we're suppressing @here and @everyone mentions
		if self.settings.getServerStat(ctx.message.server, "SuppressMentions").lower() == "yes":
			suppress = True
		else:
			suppress = False
		
		if not member:
			msg = 'Usage: `{}profileinfo [member] [profile name]`'.format(ctx.prefix)
			await self.bot.send_message(channel, msg)
			return

		profile = None

		# name is likely to be empty unless quotes are used
		if name == None:
			# Either a name wasn't set - or it's the last section
			if type(member) is str:
				# It' a string - the hope continues
				# Let's search for a name at the beginning - and a profile at the end
				parts = member.split()
				for j in range(len(parts)):
					# Reverse search direction
					i = len(parts)-1-j
					memFromName = None
					foundProf   = False
					# Name = 0 up to i joined by space
					nameStr    = ' '.join(parts[0:i+1])
					# Profile = end of name -> end of parts joined by space
					profileStr = ' '.join(parts[i+1:])
					memFromName = DisplayName.memberForName(nameStr, ctx.message.server)
					if memFromName:
						# We got a member - let's check for a profile
						linkList = self.settings.getUserStat(memFromName, server, "Profiles")
						if not linkList or linkList == []:
							pass

						for alink in linkList:
							if alink['Name'].lower() == profileStr.lower():
								# Found the link - return it.
								profile = alink
								break

		if not profile:
			# Check if there is no member specified
			linkList = self.settings.getUserStat(author, server, "Profiles")
			if not linkList or linkList == []:
				pass

			for alink in linkList:
				if alink['Name'].lower() == member.lower():
					# Found the link - return it.
					profile = alink

		if not profile:
			# At this point - we've exhausted our search
			msg = 'Sorry, I couldn\'t find that user/profile.'
			await self.bot.send_message(channel, msg)
			return
		
		# We have a profile
		currentTime = int(time.time())
		msg = '**{}:**'.format(profile['Name'])
		try:
			createdTime = int(profile['Created'])
			timeString  = ReadableTime.getReadableTimeBetween(createdTime, currentTime)
			msg = '{}\nCreated : *{}* ago'.format(msg, timeString)
		except KeyError as e:
			msg = '{}\nCreated : `UNKNOWN`'.format(msg)
		try:
			createdTime = profile['Updated']
			createdTime = int(createdTime)
			timeString  = ReadableTime.getReadableTimeBetween(createdTime, currentTime)
			msg = '{}\nUpdated : *{}* ago'.format(msg, timeString)
		except:
			pass
		# Check for suppress
		if suppress:
			msg = Nullify.clean(msg)
		await self.bot.send_message(channel, msg)
		return


	@commands.command(pass_context=True)
	async def profiles(self, ctx, *, member : str = None):
		"""List all profiles in the passed user's profile list."""
		
		channel = ctx.message.channel
		author  = ctx.message.author
		server  = ctx.message.server

		# Check if we're suppressing @here and @everyone mentions
		if self.settings.getServerStat(ctx.message.server, "SuppressMentions").lower() == "yes":
			suppress = True
		else:
			suppress = False

		if not member:
			member = author
		else:
			newMember = DisplayName.memberForName(member, server)
			if not newMember:
				# no member found by that name
				msg = 'I couldn\'t find *{}* on this server.'.format(member)
				# Check for suppress
				if suppress:
					msg = Nullify.clean(msg)
				await self.bot.send_message(channel, msg)
				return
			else:
				member = newMember

		# We have a member here
		
		linkList = self.settings.getUserStat(member, server, "Profiles")
		if linkList == None or linkList == []:
			msg = '*{}* hasn\'t added any profiles yet!  They can do so with the `{}addprofile "[profile name]" [url]` command!'.format(DisplayName.name(member), ctx.prefix)
			await self.bot.send_message(channel, msg)
			return
			
		# Sort by link name
		linkList = sorted(linkList, key=itemgetter('Name'))
		linkText = "*{}'s* Profiles:\n\n".format(DisplayName.name(member))
		for alink in linkList:
			linkText = '{}*{}*, '.format(linkText, alink['Name'])

		# Check for suppress
		if suppress:
			linkText = Nullify.clean(linkText)

		# Speak the link list while cutting off the end ", "
		await self.bot.send_message(channel, linkText[:-2])