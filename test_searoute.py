import searoute

# Singapore to Rotterdam
origin = [103.8223, 1.2644] # lon, lat
destination = [4.4792, 51.9225]

# Calculate route
route = searoute.searoute(origin, destination)

print("Props:", route['properties'])
print("Route coords:", route['geometry']['coordinates'][:5])
